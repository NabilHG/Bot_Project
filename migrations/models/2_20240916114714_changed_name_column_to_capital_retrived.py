from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `operations` RENAME COLUMN `capital_gained` TO `capital_retrived`;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `operations` RENAME COLUMN `capital_retrived` TO `capital_gained`;"""
