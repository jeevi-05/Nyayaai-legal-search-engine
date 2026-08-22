from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from loguru import logger

from app.core.config import get_settings
from app.core.database import engine, Base, SessionLocal

from app.api import (
    auth,
    users,
    documents,
    dashboard,
    health,
    research,
    judgment_comparison,
    judge,
)

from app.services import dataset_loader


settings = get_settings()



@asynccontextmanager
async def lifespan(app: FastAPI):

    # Startup
    logger.info(
        "Starting {} [{}]",
        settings.APP_NAME,
        settings.APP_ENV
    )

    Base.metadata.create_all(
        bind=engine
    )

    logger.info(
        "Database tables ensured"
    )


    db = SessionLocal()

    try:

        dataset_loader.load_all(db)

    except Exception as e:

        logger.error(
            "Dataset loading failed: {}",
            e
        )

    finally:

        db.close()


    yield


    # Shutdown

    logger.info(
        "Shutting down {}",
        settings.APP_NAME
    )




app = FastAPI(

    title=settings.APP_NAME,

    version="1.0.0",

    docs_url="/docs",

    redoc_url="/redoc",

    lifespan=lifespan
)



# -----------------------------
# CORS CONFIGURATION
# -----------------------------

if settings.APP_ENV == "development":

    cors_origins = ["*"]

    allow_credentials = False

else:

    cors_origins = settings.allowed_origins_list

    allow_credentials = True



app.add_middleware(

    CORSMiddleware,

    allow_origins=cors_origins,

    allow_credentials=allow_credentials,

    allow_methods=["*"],

    allow_headers=["*"],

    expose_headers=["*"]

)



# -----------------------------
# API ROUTERS
# -----------------------------

API_PREFIX = "/api"



app.include_router(
    health.router,
    prefix=API_PREFIX
)


app.include_router(
    auth.router,
    prefix=API_PREFIX
)


app.include_router(
    users.router,
    prefix=API_PREFIX
)


app.include_router(
    documents.router,
    prefix=API_PREFIX
)


app.include_router(
    research.router,
    prefix=API_PREFIX
)


app.include_router(
    dashboard.router,
    prefix=API_PREFIX
)

app.include_router(
    judgment_comparison.router,
    prefix=API_PREFIX
)

app.include_router(
    judge.router,
    prefix=API_PREFIX
)




# -----------------------------
# EXCEPTION HANDLERS
# -----------------------------


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError
):

    errors = "; ".join(

        f"{'.'.join(str(x) for x in e['loc'])}: {e['msg']}"

        for e in exc.errors()

    )


    return JSONResponse(

        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,

        content={

            "success": False,

            "message": errors,

            "data": None

        }

    )




@app.exception_handler(HTTPException)
async def http_exception_handler(
    request: Request,
    exc: HTTPException
):

    return JSONResponse(

        status_code=exc.status_code,

        content={

            "success": False,

            "message": exc.detail,

            "data": None

        }

    )




@app.exception_handler(Exception)
async def unhandled_exception_handler(
    request: Request,
    exc: Exception
):

    logger.error(

        "Unhandled exception {} {} : {}",

        request.method,

        request.url,

        exc

    )


    return JSONResponse(

        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,

        content={

            "success": False,

            "message": str(exc),

            "data": None

        }

    )
