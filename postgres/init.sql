CREATE TABLE IF NOT EXISTS users
(
    id    uuid PRIMARY KEY,
    name  varchar(256),
    email varchar(256)
);

CREATE TABLE IF NOT EXISTS orders
(
    id              uuid primary key,
    user_id         uuid references users (id),
    total_count     decimal,
    order_timestamp integer
)