import { logger } from './logger.js';
import { showNotifyModal } from '../ui/modals.js';

// Utility function for handling ajax errors in a consistent way across the module. 

export function handleAjaxError({ err, context }) {
    // Extract useful info
    const statusCode = err.jqXHR?.status;
    const responseText = err.jqXHR?.responseText;
    const textStatus = err.textStatus;
    const errorThrown = err.errorThrown;

    // Log (centralised)
    logger.error("AJAX Error:", {
        statusCode,
        textStatus,
        errorThrown,
        responseText,
        context
    });

    // Delegate UI update
    showError({
        statusCode,
        message:
            typeof errorThrown === "string"
                ? errorThrown
                : errorThrown?.error || "An unexpected error occurred",
        context,
        }, responseText);
}

function showError(err) {
    // This is a very basic error display function. We can make it more sophisticated later if we want to
    let errorMessage=`${err.context}. An error occurred: ${err.statusCode} - ${err.message}.`;
    showNotifyModal(errorMessage, "Error");
};