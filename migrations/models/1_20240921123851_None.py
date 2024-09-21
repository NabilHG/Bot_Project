from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS `shares` (
    `id` BIGINT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `ticker` VARCHAR(10) NOT NULL
) CHARACTER SET utf8mb4;
CREATE TABLE IF NOT EXISTS `users` (
    `id` BIGINT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `name` VARCHAR(50) NOT NULL,
    `username` VARCHAR(50) NOT NULL,
    `phone` VARCHAR(9) NOT NULL,
    `register_date` DATETIME(6) NOT NULL  DEFAULT CURRENT_TIMESTAMP(6),
    `expeling_date` DATETIME(6),
    `investor_profile` DOUBLE NOT NULL,
    `is_admin` BOOL NOT NULL,
    `belongs_to` BIGINT,
    `is_lictor` BOOL
) CHARACTER SET utf8mb4;
CREATE TABLE IF NOT EXISTS `wallets` (
    `id` BIGINT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `initial_capital` DOUBLE NOT NULL,
    `current_capital` DOUBLE,
    `gain_capital` DOUBLE,
    `profit` DOUBLE,
    `max_drawdown` DOUBLE,
    `peak_capital` DOUBLE,
    `number_of_operations` INT,
    `user_id` BIGINT NOT NULL,
    CONSTRAINT `fk_wallets_users_25f937b3` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) CHARACTER SET utf8mb4;
CREATE TABLE IF NOT EXISTS `operations` (
    `id` BIGINT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `ticker` VARCHAR(10) NOT NULL,
    `buy_date` DATETIME(6) NOT NULL,
    `sell_date` DATETIME(6),
    `capital_invested` DOUBLE NOT NULL,
    `capital_retrived` DOUBLE,
    `purchased_price` DOUBLE,
    `status` VARCHAR(10) NOT NULL,
    `wallet_id` BIGINT NOT NULL,
    CONSTRAINT `fk_operatio_wallets_d14ae7cc` FOREIGN KEY (`wallet_id`) REFERENCES `wallets` (`id`) ON DELETE CASCADE
) CHARACTER SET utf8mb4;
CREATE TABLE IF NOT EXISTS `wallet_share` (
    `id` BIGINT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `share_id` BIGINT NOT NULL,
    `wallet_id` BIGINT NOT NULL,
    UNIQUE KEY `uid_wallet_shar_wallet__9af32c` (`wallet_id`, `share_id`),
    CONSTRAINT `fk_wallet_s_shares_c9931463` FOREIGN KEY (`share_id`) REFERENCES `shares` (`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_wallet_s_wallets_ddb320d7` FOREIGN KEY (`wallet_id`) REFERENCES `wallets` (`id`) ON DELETE CASCADE
) CHARACTER SET utf8mb4;
CREATE TABLE IF NOT EXISTS `aerich` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `version` VARCHAR(255) NOT NULL,
    `app` VARCHAR(100) NOT NULL,
    `content` JSON NOT NULL
) CHARACTER SET utf8mb4;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        """
