const BASE_PATH = process.env.BASE_PATH || ""

export function url_for(path) {
    console.log()
    if(path.startsWith("/")) {
        return BASE_PATH + path;
    }
    return path;
}