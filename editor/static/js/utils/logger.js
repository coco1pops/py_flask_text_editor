export const config = {
    DEBUG: true
};

export const logger = {
    log: (...args) => config.DEBUG && console.log(...args),
    warn: (...args) => config.DEBUG && console.warn(...args),
    error: (...args) => console.error(...args)
};