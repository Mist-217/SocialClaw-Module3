"""
pytest 测试配置和 fixture
"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.models import Base
from app.core.database import get_db
from app.main import app
from app.models.user import User
from app.models.connected_agent import ConnectedAgent


# 使用内存 SQLite 数据库进行测试
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"


@pytest.fixture(scope="function")
def db():
    """创建数据库会话 fixture"""
    # 创建内存数据库引擎
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    # 创建所有表
    Base.metadata.create_all(bind=engine)
    # 创建会话
    session = Session(bind=engine)

    yield session

    # 测试结束后回滚并关闭
    session.rollback()
    session.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def test_db(db):
    """兼容现有测试代码的别名"""
    yield db


@pytest.fixture
def test_user1(db):
    """创建测试用户 1"""
    user = User(
        user_id="test_user_1",
        username="testuser1",
        email="test1@example.com"
    )
    db.add(user)
    db.commit()
    return user


@pytest.fixture
def test_user2(db):
    """创建测试用户 2"""
    user = User(
        user_id="test_user_2",
        username="testuser2",
        email="test2@example.com"
    )
    db.add(user)
    db.commit()
    return user


@pytest.fixture
def test_agent1(db, test_user1):
    """创建测试 Agent 1"""
    agent = ConnectedAgent(
        agent_id="test_agent_1",
        user_id=test_user1.user_id,
        name="Test Agent 1",
        description="Test agent one"
    )
    db.add(agent)
    db.commit()
    return agent


@pytest.fixture
def test_agent2(db, test_user2):
    """创建测试 Agent 2"""
    agent = ConnectedAgent(
        agent_id="test_agent_2",
        user_id=test_user2.user_id,
        name="Test Agent 2",
        description="Test agent two"
    )
    db.add(agent)
    db.commit()
    return agent
