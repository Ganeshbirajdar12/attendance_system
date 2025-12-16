create database attendance_system1;
use attendance_system1;
show tables;
select * from attendance;
create table admin_auth(
	id int primary key not null auto_increment,
    username varchar (260),
    password varchar(230),
    email varchar(200)
);
CREATE TABLE Programs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    program_name VARCHAR(100) NOT NULL,
    program_code VARCHAR(20),
    duration VARCHAR(20),
    department VARCHAR(100),
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE Teachers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    program_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (program_id) REFERENCES Programs(id) ON DELETE CASCADE
);


CREATE TABLE Teachers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP);
    
    CREATE TABLE Classes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    class_name VARCHAR(100) NOT NULL,
    program VARCHAR(100) NOT NULL,
    year VARCHAR(50),
    teacher VARCHAR(100),
    division VARCHAR(10),
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
;

SELECT program_name FROM Programs;
SELECT name FROM Teachers;

SHOW CREATE TABLE Programs;
SHOW CREATE TABLE Teachers;

SHOW CREATE TABLE Classes;

CREATE TABLE students (
    student_id INT AUTO_INCREMENT PRIMARY KEY,
    roll_number VARCHAR(20) NOT NULL UNIQUE,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100),
    gender ENUM('Male', 'Female', 'Other'),
    dob DATE,
    email VARCHAR(150) UNIQUE,
    phone VARCHAR(15),
    address TEXT,

    class_id INT NOT NULL,
    program_id INT NOT NULL,
    admission_date DATE DEFAULT (CURRENT_DATE),

    status ENUM('Active', 'Inactive') DEFAULT 'Active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    FOREIGN KEY (class_id) REFERENCES classes(id),
    FOREIGN KEY (program_id) REFERENCES programs(id)
);

CREATE TABLE attendance (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT,
    attendance_date DATE,
    status ENUM('Present','Absent'),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(student_id, attendance_date)
);







