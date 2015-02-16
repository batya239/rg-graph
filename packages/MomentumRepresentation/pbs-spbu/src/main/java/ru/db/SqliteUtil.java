package ru.db;

import org.springframework.jdbc.core.JdbcTemplate;

/**
 * @author dima
 */
public class SqliteUtil {

    private final static String TASKS_SCHEMA_DEFINITION = "CREATE TABLE tasks (id INTEGER PRIMARY KEY AUTOINCREMENT, task_name NOT_NULL, worker TEXT, start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP, end_time TIMESTAMP, UNIQUE(task_name))";
    private final static String WORKERS_SCHEMA_DEFINITION = "CREATE TABLE workers (worker_name TEXT, ping_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP)";

    public static void createSchema(JdbcTemplate jdbcTemplate) {
        jdbcTemplate.execute(TASKS_SCHEMA_DEFINITION);
        jdbcTemplate.execute(WORKERS_SCHEMA_DEFINITION);
    }
}
