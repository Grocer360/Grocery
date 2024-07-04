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

CREATE TABLE Interactions (
    bar_code VARCHAR(255) NOT NULL,
    user_name VARCHAR(255) NOT NULL,
    time_stamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY(user_name, bar_codeوtime_stamp),
    FOREIGN KEY (bar_code) REFERENCES Products(bar_code),
    FOREIGN KEY (user_name) REFERENCES Users(user_name)
);



