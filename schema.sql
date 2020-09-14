CREATE TABLE users (
	id INTEGER PRIMARY KEY,
	username TEXT UNIQUE NOT NULL,
	hash TEXT NOT NULL
	);

CREATE TABLE projects (
	id INTEGER PRIMARY KEY,
	owner INTEGER NOT NULL,
	name TEXT NOT NULL,
	description TEXT,
	FOREIGN KEY (owner) REFERENCES users (id)
	);

CREATE TABLE tasks (
	task_id INTEGER PRIMARY KEY,
	task TEXT NOT NULL,
	deadline TEXT,
	project_id INT NOT NULL,
	FOREIGN KEY (project_id) REFERENCES projects (id)
	);

CREATE TABLE completed (
	task TEXT NOT NULL,
	date TEXT NOT NULL,
	user_id INTEGER PRIMARY KEY
	);