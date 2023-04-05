import setuptools

EXTRAS_REQUIRE = {
    "tests": [
        "pytest==7.1.3",
        "async_asgi_testclient==1.4.10",
        "pytest-asyncio==0.19.0",
        "pytest-repeat==0.9.1",
        "pytest-order==1.0.1",
    ],
    "lint": ["pylint[spelling]==2.14.0", "flake8==4.0.1"],
    "deploy": [
        "virtualenv==20.16.5",
        "gunicorn==20.1.0",
        "uvicorn==0.20.0",
        "alembic==1.8.1",
    ],
    "dev": [
        "rope==0.23.0",
        "isort==5.10.1",
        "yapf==0.32.0",
    ],
}
EXTRAS_REQUIRE["dev"] += \
    EXTRAS_REQUIRE["tests"] + \
    EXTRAS_REQUIRE["lint"] +  \
    EXTRAS_REQUIRE["deploy"]

setuptools.setup(
    name="rockps",
    version="0.0.1",
    install_requires=[
        "fastapi==0.83.0",
        "asyncpg==0.26.0",
        "python-jose[cryptography]==3.3.0",
        "bcrypt==3.2.0",
        "environs==9.5.0",
        "psycopg2-binary==2.9.1",
        "httpx==0.23.0",
        "sqlalchemy==2.0.8",
        "python-multipart==0.0.5",
        "loguru==0.6.0",
    ],
    package_dir={"": "src"},
    extras_require=EXTRAS_REQUIRE,
    url="https://github.com/Actticus/rockps",
    author="saltytimofey@gmail.com",
)
