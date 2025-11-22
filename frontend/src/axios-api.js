import axios from 'axios'

const getAPI = axios.create({
    baseURL: 'http://localhost:8000',   //Nos comunicamos con la api de django
    timeout: 1000,  
})

export {getAPI}