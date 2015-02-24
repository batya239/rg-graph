package ru.db;

import org.apache.commons.io.IOUtils;
import org.apache.log4j.Logger;
import org.jetbrains.annotations.NotNull;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.jdbc.core.JdbcTemplate;

import java.io.File;
import java.io.IOException;
import java.util.concurrent.Executors;
import java.util.concurrent.ScheduledExecutorService;
import java.util.concurrent.TimeUnit;

/**
 * @author dima
 */
public class Worker {
    private static final String KILL_FILE = "kill";

    @NotNull
    private final String hostName;
    @NotNull
    private final Logger log;
    private final File baseDir;
    private final ScheduledExecutorService heartBeat;
    private volatile boolean stop = false;
    @Autowired
    private JdbcTemplate jdbcTemplate;

    public Worker(String baseDir) {
        hostName = ApplicationConfig.getHostName();
        log = Logger.getLogger(hostName);
        this.baseDir = new File(baseDir);
        if (!this.baseDir.exists() && !this.baseDir.mkdirs()) {
            throw new RuntimeException("Can't create dir " + baseDir);
        }
        log.info("Worker on " + hostName + " started");
        heartBeat = Executors.newScheduledThreadPool(1);
    }

    public void start() {
        long isExist = jdbcTemplate.queryForObject("SELECT COUNT(*) FROM workers WHERE worker_name = ?", Long.class, hostName);
        if (isExist == 0) {
            jdbcTemplate.update("INSERT INTO workers (worker_name) VALUES (?)", hostName);
        }
        heartBeat.scheduleWithFixedDelay(() -> {
            log.info("Worker " + hostName + " is alive");
            jdbcTemplate.update("UPDATE workers SET ping_time = datetime('now') WHERE worker_name = ?", hostName);
        }, 0, 10, TimeUnit.SECONDS);
        Runtime.getRuntime().addShutdownHook(new Thread(() -> {
            log.info("Heartbeat thread is shutdown now on " + hostName);
            stop = true;
            heartBeat.shutdownNow();
        }));
        while (!stop) {
            sleep();
            findAndExecuteTask();
        }
    }

    private void findAndExecuteTask() {
        try {
            for (File file : baseDir.listFiles()) {
                if (file.isDirectory()) {
                    TaskStatus status = TaskStatus.getOrNull(file);
                    if (status == null) {
                        log.info("Task " + file.getName() + " status is null");
                        continue;
                    }
                    if (status == TaskStatus.NEW) {
                        String taskName = file.getName();
                        int updatedRows = jdbcTemplate.update("INSERT OR IGNORE INTO tasks(task_name, worker) VALUES(?, ?)", taskName, hostName);
                        if (updatedRows != 0) {
                            execute(file);
                        }
                    }
                }
            }
        } catch (Exception e) {
            log.error(e);
        }
    }

    private void execute(File task) {
        TaskStatus.writeStatus(task, TaskStatus.RUN);
        log.info("Start task " + task.getName() + " on " + hostName);
        Process process = null;
        try {
            process = new ProcessBuilder("./job_executable").directory(task).redirectOutput(new File(task, "output.txt")).start();
            while (process.isAlive()) {
                if (isKilled(task)) {
                    TaskStatus.writeStatus(task, TaskStatus.KILLED);
                    log.info(String.format("Task %s is killed while executing on %s", task.getName(), hostName));
                    process.destroy();
                    return;
                }
                log.info(String.format("Task %s in progress on %s", task.getName(), hostName));
                sleep();
            }
            if (process.exitValue() == 0) {
                TaskStatus.writeStatus(task, TaskStatus.DONE);
                log.info(String.format("Task %s is done on %s", task.getName(), hostName));
                updateEndTime(task);
            } else {
                throw new IOException();
            }
        } catch (IOException e) {
            TaskStatus.writeStatus(task, TaskStatus.FAILED);
            String error;
            try {
                error = process == null ? "" : IOUtils.toString(process.getErrorStream());
            } catch (IOException e1) {
                error = "";
            }
            updateEndTime(task);
            log.error(String.format("Task %s failed on %s: %s", task.getName(), hostName, error));
        }
    }

    private int updateEndTime(File task) {
        return jdbcTemplate.update("UPDATE tasks SET end_time = datetime('now') WHERE end_time IS NULL AND worker = ? AND task_name = ?", hostName, task.getName());
    }

    private void sleep() {
        try {
            Thread.sleep(10000);
        } catch (InterruptedException e) {
            log.error(e);
            throw new RuntimeException(e);
        }
    }

    private static boolean isKilled(final File task) {
        return new File(task, KILL_FILE).exists();
    }
}
