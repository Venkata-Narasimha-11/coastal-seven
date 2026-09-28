-- =============================================================================
-- SQL Foundations Reference Queries: CLI Task Manager
-- Demonstrates: INNER JOIN, LEFT JOIN, GROUP BY, HAVING, Aggregate Functions,
--               Subqueries, Filtering, and Performance Analysis.
-- =============================================================================

-- -----------------------------------------------------------------------------
-- 1. JOINS (Connecting Relational Entities)
-- -----------------------------------------------------------------------------

-- Query 1.1: INNER JOIN
-- Returns only tasks that have an assigned category.
SELECT 
    t.id AS task_id,
    t.title,
    t.status,
    t.priority,
    c.name AS category_name,
    c.description AS category_description
FROM tasks t
INNER JOIN categories c ON t.category_id = c.id
ORDER BY t.id ASC;

-- Query 1.2: LEFT JOIN (Preserving Uncategorized Tasks)
-- Returns all tasks, even those where category_id is NULL.
SELECT 
    t.id AS task_id,
    t.title,
    t.status,
    t.priority,
    COALESCE(c.name, 'Uncategorized') AS category_name
FROM tasks t
LEFT JOIN categories c ON t.category_id = c.id
ORDER BY t.id ASC;

-- Query 1.3: LEFT JOIN from Categories (Finding Empty Categories)
-- Lists every category and the tasks assigned to it.
SELECT 
    c.name AS category_name,
    t.id AS task_id,
    t.title AS task_title,
    t.status
FROM categories c
LEFT JOIN tasks t ON c.id = t.category_id
ORDER BY c.name, t.id;

-- Query 1.4: Many-to-Many JOIN with Aggregation (Tags per Task)
SELECT 
    t.id AS task_id,
    t.title,
    c.name AS category_name,
    COALESCE(STRING_AGG(tg.name, ', ' ORDER BY tg.name), 'No Tags') AS tags
FROM tasks t
LEFT JOIN categories c ON t.category_id = c.id
LEFT JOIN task_tags tt ON t.id = tt.task_id
LEFT JOIN tags tg ON tt.tag_id = tg.id
GROUP BY t.id, t.title, c.name
ORDER BY t.id;

-- -----------------------------------------------------------------------------
-- 2. AGGREGATE FUNCTIONS & GROUP BY
-- -----------------------------------------------------------------------------

-- Query 2.1: Overall Task Metrics (Aggregate Functions)
SELECT 
    COUNT(*) AS total_tasks,
    COUNT(CASE WHEN status = 'completed' THEN 1 END) AS completed_tasks,
    COUNT(CASE WHEN status = 'pending' THEN 1 END) AS pending_tasks,
    COUNT(CASE WHEN status = 'in_progress' THEN 1 END) AS in_progress_tasks,
    MIN(due_date) AS earliest_due_date,
    MAX(due_date) AS latest_due_date
FROM tasks;

-- Query 2.2: Task Count Grouped by Status
SELECT 
    status,
    COUNT(*) AS task_count
FROM tasks
GROUP BY status
ORDER BY task_count DESC;

-- Query 2.3: Task Count Grouped by Priority
SELECT 
    priority,
    COUNT(*) AS task_count
FROM tasks
GROUP BY priority
ORDER BY 
    CASE priority 
        WHEN 'urgent' THEN 1 
        WHEN 'high' THEN 2 
        WHEN 'medium' THEN 3 
        WHEN 'low' THEN 4 
    END;

-- Query 2.4: Category Breakdown with Detailed Aggregates
SELECT 
    c.id AS category_id,
    c.name AS category_name,
    COUNT(t.id) AS total_tasks,
    COUNT(CASE WHEN t.status = 'completed' THEN 1 END) AS completed_tasks,
    COUNT(CASE WHEN t.status != 'completed' THEN 1 END) AS active_tasks
FROM categories c
LEFT JOIN tasks t ON c.id = t.category_id
GROUP BY c.id, c.name
ORDER BY total_tasks DESC;

-- -----------------------------------------------------------------------------
-- 3. GROUP BY WITH HAVING CLAUSE
-- (HAVING filters groups AFTER aggregation, unlike WHERE which filters rows BEFORE)
-- -----------------------------------------------------------------------------

-- Query 3.1: Categories with at least 2 active (uncompleted) tasks
SELECT 
    c.name AS category_name,
    COUNT(t.id) AS total_tasks,
    COUNT(CASE WHEN t.status != 'completed' THEN 1 END) AS active_tasks
FROM categories c
INNER JOIN tasks t ON c.id = t.category_id
GROUP BY c.name
HAVING COUNT(CASE WHEN t.status != 'completed' THEN 1 END) >= 2
ORDER BY active_tasks DESC;

-- Query 3.2: Priorities that have more than 1 task currently pending
SELECT 
    priority,
    COUNT(*) AS pending_count
FROM tasks
WHERE status = 'pending'
GROUP BY priority
HAVING COUNT(*) > 1
ORDER BY pending_count DESC;

-- Query 3.3: Categories that have a 100% completion rate (all tasks completed)
SELECT 
    c.name AS category_name,
    COUNT(t.id) AS total_tasks,
    COUNT(CASE WHEN t.status = 'completed' THEN 1 END) AS completed_tasks
FROM categories c
INNER JOIN tasks t ON c.id = t.category_id
GROUP BY c.name
HAVING COUNT(t.id) > 0 AND COUNT(CASE WHEN t.status = 'completed' THEN 1 END) = COUNT(t.id);

-- -----------------------------------------------------------------------------
-- 4. OVERDUE TASKS & DATE FILTERING
-- -----------------------------------------------------------------------------

SELECT 
    t.id,
    t.title,
    t.due_date,
    t.priority,
    c.name AS category_name,
    CURRENT_DATE - t.due_date AS days_overdue
FROM tasks t
LEFT JOIN categories c ON t.category_id = c.id
WHERE t.status != 'completed' AND t.due_date < CURRENT_DATE
ORDER BY t.due_date ASC;
