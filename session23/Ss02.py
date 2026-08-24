from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer

app = FastAPI()


# =========================
# CORS
# =========================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


# =========================
# USERS
# =========================

TOKENS = {
    "admin-token": {
        "username": "admin01",
        "role": "admin",
        "is_active": True,
    },

    "user-token": {
        "username": "student01",
        "role": "user",
        "is_active": True,
    },

    "locked-token": {
        "username": "locked01",
        "role": "user",
        "is_active": False,
    },
}


# =========================
# MIDDLEWARE
# =========================

@app.middleware("http")
async def authentication_middleware(request, call_next):

    # Cho phép CORS Preflight
    if request.method == "OPTIONS":
        response = await call_next(request)

        response.headers["X-System-Name"] = (
            "Learning Management System"
        )

        return response

    # /health được truy cập công khai
    if request.url.path == "/health":
        response = await call_next(request)

        response.headers["X-System-Name"] = (
            "Learning Management System"
        )

        return response

    # Các API còn lại yêu cầu Authorization
    if "authorization" not in request.headers:
        return JSONResponse(
            status_code=401,
            content={
                "detail": "Authorization header is required"
            }
        )

    response = await call_next(request)

    response.headers["X-System-Name"] = (
        "Learning Management System"
    )

    return response


# =========================
# CURRENT USER
# =========================

def get_current_user(
    token: str = Depends(oauth2_scheme)
):

    user = TOKENS.get(token)

    if user is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )

    # Tài khoản bị khóa
    if not user["is_active"]:
        raise HTTPException(
            status_code=401,
            detail="User account is inactive"
        )

    return user


# =========================
# ADMIN
# =========================

def require_admin(
    current_user: dict = Depends(get_current_user)
):

    # Chỉ ADMIN được phép
    if current_user["role"] != "admin":
        raise HTTPException(
            status_code=403,
            detail="Admin permission required"
        )

    return current_user


# =========================
# HEALTH
# =========================

@app.get("/health")
def health_check():

    return {
        "status": "UP"
    }


# =========================
# GET COURSES
# =========================

@app.get("/courses")
def get_courses(
    current_user: dict = Depends(get_current_user)
):

    return {
        "items": [
            {
                "id": 1,
                "name": "FastAPI Basic"
            },
            {
                "id": 2,
                "name": "FastAPI Security"
            }
        ]
    }


# =========================
# DELETE COURSE
# ADMIN ONLY
# =========================

@app.delete("/admin/courses/{course_id}")
def delete_course(
    course_id: int,
    current_user: dict = Depends(require_admin)
):

    return {
        "message": f"Course {course_id} has been deleted",
        "deleted_by": current_user["username"]
    }