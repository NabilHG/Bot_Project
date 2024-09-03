from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `operations` ADD `status` VARCHAR(10) NOT NULL;
        ALTER TABLE `operations` MODIFY COLUMN `capital_gained` DOUBLE;
        ALTER TABLE `operations` MODIFY COLUMN `sell_date` DATETIME(6);
        ALTER TABLE `wallets` MODIFY COLUMN `profit` DOUBLE;
        ALTER TABLE `wallets` MODIFY COLUMN `max_drawdown` DOUBLE;
        ALTER TABLE `wallets` MODIFY COLUMN `number_of_operations` INT;
        ALTER TABLE `wallets` MODIFY COLUMN `current_capital` DOUBLE;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `wallets` MODIFY COLUMN `profit` DOUBLE NOT NULL;
        ALTER TABLE `wallets` MODIFY COLUMN `max_drawdown` DOUBLE NOT NULL;
        ALTER TABLE `wallets` MODIFY COLUMN `number_of_operations` INT NOT NULL;
        ALTER TABLE `wallets` MODIFY COLUMN `current_capital` DOUBLE NOT NULL;
        ALTER TABLE `operations` DROP COLUMN `status`;
        ALTER TABLE `operations` MODIFY COLUMN `capital_gained` DOUBLE NOT NULL;
        ALTER TABLE `operations` MODIFY COLUMN `sell_date` DATETIME(6) NOT NULL;"""
