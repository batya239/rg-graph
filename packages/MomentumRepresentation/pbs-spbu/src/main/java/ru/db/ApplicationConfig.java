package ru.db;

import org.apache.commons.dbcp.BasicDataSource;
import org.apache.log4j.FileAppender;
import org.apache.log4j.Level;
import org.apache.log4j.Logger;
import org.apache.log4j.PatternLayout;
import org.springframework.beans.factory.config.BeanDefinition;
import org.springframework.context.annotation.AnnotationConfigApplicationContext;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.Scope;
import org.springframework.jdbc.core.JdbcTemplate;

import java.io.File;
import java.net.InetAddress;
import java.net.UnknownHostException;

/**
 * @author dima
 */
@Configuration
public class ApplicationConfig {
    private final static String SERVER_PATH = System.getProperty("user.home") + "/.server";

    @Bean(initMethod = "start")
    @Scope(BeanDefinition.SCOPE_SINGLETON)
    public Worker worker() {
        return new Worker(SERVER_PATH);
    }

    @Bean
    @Scope(BeanDefinition.SCOPE_SINGLETON)
    public JdbcTemplate jdbcTemplate() {
        BasicDataSource dataSource = new BasicDataSource();
        dataSource.setDriverClassName("org.sqlite.JDBC");
        String dbPath = SERVER_PATH + "/db";
        boolean inited = new File(dbPath).getAbsoluteFile().exists();
        dataSource.setUrl("jdbc:sqlite:" + dbPath);
        JdbcTemplate jdbcTemplate = new JdbcTemplate(dataSource);
        if (!inited) {
            SqliteUtil.createSchema(jdbcTemplate);
        }
        return jdbcTemplate;
    }

    public static void main(String[] args) {
        createFileAppender();
        new AnnotationConfigApplicationContext(ApplicationConfig.class);
    }

    public static String getHostName() {
        final String hostname;
        try {
            hostname = InetAddress.getLocalHost().getHostName();
            return hostname == null ? "unnamed" : hostname;
        } catch (UnknownHostException e) {
            Logger.getLogger(ApplicationConfig.class).error("Can't evaluate hostname");
            return "unnamed";
        }
    }

    private static void createFileAppender() {
        String hostName = getHostName();
        String fileName = hostName + ".worker.log";
        FileAppender appender = new FileAppender();
        appender.setName("WorkerFileAppender");
        appender.setLayout(new PatternLayout("%-5p %c{1} [%d] - %m%n"));
        appender.setFile(System.getProperty("user.home") + "/" + fileName);
        appender.setAppend(false);
        appender.setThreshold(Level.DEBUG);
        appender.activateOptions();
        Logger.getRootLogger().addAppender(appender);
    }
}
