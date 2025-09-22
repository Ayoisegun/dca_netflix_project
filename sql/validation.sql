SELECT
    COUNT(*) AS record_count,
    MIN(release_year) AS min_year,
    MAX(release_year) AS max_year,
    COUNT(CASE WHEN duration IS NULL OR duration = '' THEN 1 END) AS duration_issue,
    COUNT(CASE WHEN country IS NULL THEN 1 END) AS country_issue,
    COUNT(show_id) - COUNT(DISTINCT show_id) AS duplicate_ids,
    COUNT(CASE WHEN title IS NULL OR title = '' THEN 1 END) AS null_titles
FROM movies;
