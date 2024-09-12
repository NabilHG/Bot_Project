from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `operations` DROP COLUMN `capital_gained`;
        ALTER TABLE `operations` DROP COLUMN `capital_invested`;
        ALTER TABLE `wallets` DROP COLUMN `profit`;
        ALTER TABLE `wallets` DROP COLUMN `current_capital`;
        ALTER TABLE `wallets` DROP COLUMN `max_drawdown`;
        ALTER TABLE `wallets` DROP COLUMN `initial_capital`;
        ALTER TABLE `wallets` DROP COLUMN `number_of_operations`;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `wallets` ADD `profit` DOUBLE;
        ALTER TABLE `wallets` ADD `current_capital` DOUBLE;
        ALTER TABLE `wallets` ADD `max_drawdown` DOUBLE;
        ALTER TABLE `wallets` ADD `initial_capital` DOUBLE NOT NULL;
        ALTER TABLE `wallets` ADD `number_of_operations` INT;
        ALTER TABLE `operations` ADD `capital_gained` DOUBLE;
        ALTER TABLE `operations` ADD `capital_invested` DOUBLE NOT NULL;"""
