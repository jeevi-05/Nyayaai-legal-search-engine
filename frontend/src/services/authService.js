import api from "./api";


export function login(
    email,
    password
){

    return api.post(
        "/auth/login",
        {
            email,
            password
        }
    );

}



export function register(
    fullName,
    email,
    password,
    role
){

    return api.post(
        "/auth/register",
        {

            full_name: fullName,

            email,

            password,

            role

        }
    );

}

export function verifyOtp(email, otp) {
    return api.post("/auth/verify-otp", { email, otp });
}

export function resendOtp(email) {
    return api.post("/auth/resend-otp", { email });
}