package ru.db;

import java.io.File;
import java.io.IOException;
import java.util.Arrays;

/**
 * @author dima
 */
public enum TaskStatus {
    RUN,
    DONE,
    FAILED,
    NEW;

    public static TaskStatus getOrNull(final File task) {
        return Arrays.stream(values()).filter(s -> new File(task, s.getFileName()).exists()).findFirst().orElseGet(() -> null);
    }

    public static void writeStatus(File task, TaskStatus status) {
        Arrays.stream(values()).forEach(s -> new File(task, s.getFileName()).delete());
        File file = new File(task, status.getFileName());
        try {
            if (!file.createNewFile()) {
                throw new IOException("Can't create file " + file.getAbsolutePath());
            }
        } catch (IOException e) {
            throw new RuntimeException(e);
        }
    }

    private String getFileName() {
        return "." + name().toLowerCase();
    }
}
