-- =============================================================================
-- Relational Schema: CLI Task Manager
-- Database: PostgreSQL 17+
-- Demonstrates: Primary/Foreign Keys, Unique/Check Constraints, B-Tree Indexes,
--               Cascading Rules, and Relational Normalization.
-- =============================================================================

-- Clean up existing tables if recreating (order matters due to foreign keys)
DROP TABLE IF EXISTS task_tags CASCADE;
DROP TABLE IF EXISTS tags CASCADE;
DROP TABLE IF EXISTS tasks CASCADE;
DROP TABLE IF EXISTS categories CASCADE;

-- -----------------------------------------------------------------------------
-- 1. Categories Table (One-to-Many parent with Tasks)
-- -----------------------------------------------------------------------------
CREATE TABLE categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- -----------------------------------------------------------------------------
-- 2. Tasks Table (Core Entity)
-- -----------------------------------------------------------------------------
CREATE TABLE tasks (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    category_id INT REFERENCES categories(id) ON DELETE SET NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'pending' 
        CHECK (status IN ('pending', 'in_progress', 'completed', 'archived')),
    priority VARCHAR(10) NOT NULL DEFAULT 'medium' 
        CHECK (priority IN ('low', 'medium', 'high', 'urgent')),
    due_date DATE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- -----------------------------------------------------------------------------
-- 3. Tags Table (Many-to-Many Entity)
-- -----------------------------------------------------------------------------
CREATE TABLE tags (
    id SERIAL PRIMARY KEY,
    name VARCHAR(30) NOT NULL UNIQUE
);

-- -----------------------------------------------------------------------------
-- 4. Task_Tags Junction Table (Many-to-Many Relationship)
-- -----------------------------------------------------------------------------
CREATE TABLE task_tags (
    task_id INT NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    tag_id INT NOT NULL REFERENCES tags(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (task_id, tag_id)
);

-- -----------------------------------------------------------------------------
-- 5. Indexes for Query Performance Optimization
-- -----------------------------------------------------------------------------
-- Index on foreign key for faster JOINs between tasks and categories
CREATE INDEX idx_tasks_category_id ON tasks(category_id);

-- Index on task status for filtering pending/completed tasks
CREATE INDEX idx_tasks_status ON tasks(status);

-- Index on task priority for ordering and high-priority filters
CREATE INDEX idx_tasks_priority ON tasks(priority);

-- Index on due_date for range filtering and overdue task detection
CREATE INDEX idx_tasks_due_date ON tasks(due_date);

-- Index on junction table foreign key for reverse tag lookups
CREATE INDEX idx_task_tags_tag_id ON task_tags(tag_id);
