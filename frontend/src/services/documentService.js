import api from "./api";


export const getAllDocuments = () =>
    api.get("/documents");


export const getByCategory = (category) =>
    api.get(`/documents/category/${category}`);


export const getCount = () =>
    api.get("/documents/count");


export const uploadDocument = (formData) =>
    api.post(
        "/documents/upload",
        formData,
        {
            headers:{
                "Content-Type":"multipart/form-data"
            }
        }
    );


export const deleteDocument = (id) =>
    api.delete(`/documents/${id}`);