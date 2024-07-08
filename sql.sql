CREATE TABLE Users (
    user_name VARCHAR(255) PRIMARY KEY,
    password VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL,
    working_hours INT DEFAULT 0,
    logged_in BOOLEAN DEFAULT FALSE,
    img VARCHAR(100),
    time_stamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE Products (
    bar_code VARCHAR(255) PRIMARY KEY,
    prod_name VARCHAR(255) NOT NULL,
    quantity INT NOT NULL,
    category VARCHAR(255) NOT NULL,
    price DECIMAL(10, 2) NOT NULL
);




