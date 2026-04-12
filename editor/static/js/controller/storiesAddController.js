import { resizeTextarea, updateLabel, displaySafetySettings } from "../ui/storiesUI.js";
import { getSysInt } from "../api/storiesAPI.js";

document.addEventListener("DOMContentLoaded", function () {
    const raw = document.getElementById('isadmin-data').dataset.isadmin;
    const isadmin = JSON.parse(raw);

    displaySafetySettings(isadmin);

    document.getElementById('applySysInt').addEventListener('click', event => {
        pickSysInt();
        document.getElementById('paramsSaved').value = "True";
    });

    document.addEventListener('input', event => {
        if (event.target.classList.contains('entry-textarea')) {
            resizeTextarea(event.target);
        }
        else if (event.target.classList.contains('form-range')) {
            updateLabel(event.target.id);
            generateSummary();
        }
    });

    document.getElementById('closeModal').addEventListener('click', event => {
        buildSysIntOptions();
    });
});

function buildSysIntOptions(sysInt) {
    const repetition = parseFloat(document.getElementById("repetition").value);
    const pacing = parseFloat(document.getElementById("pacing").value);
    const style = parseFloat(document.getElementById("style").value);  

    // Add repetition guidance

    if (repetition > 1.3) {
        sysInt = sysInt + "\nAvoid repeating distinctive words or imagery."
    }
    else if (repetition < 0.7) {
        sysInt = sysInt + "\nRepetition is acceptable for thematic effect."
    }

    // Add pacing guidance

    if (pacing > 1.3) {
        sysInt = sysInt + "\nUse shorter sentences and increase narrative momentum."
    } else if (pacing < 0.7) {
        sysInt = sysInt + "\nUse richer description and slower scene development."
    }

    // Add Style strength guidance
    if (style > 1.3) {
        sysInt = sysInt + "\nLean strongly into a distinctive narrative voice."
    } else if (style < 0.7) {
        sysInt = sysInt + "\nKeep the prose neutral and unobtrusive."
    }
    return sysInt;
}

export function generateSummary() {
    const temp = parseFloat(document.getElementById("temperature").value);
    const rep = parseFloat(document.getElementById("repetition").value);
    const pace = parseFloat(document.getElementById("pacing").value);

    let creativity =
        temp < 0.6 ? "Controlled" :
            temp < 0.95 ? "Balanced" :
                "Highly creative";

    let repText =
        rep < 0.7 ? "may reuse phrasing" :
            rep < 1.3 ? "moderate variation" :
                "actively avoids repetition";

    let pacingText =
        pace < 0.7 ? "slow and descriptive" :
            pace < 1.3 ? "steady pacing" :
                "fast and dynamic";

    summaryBox.textContent =
        `${creativity} prose, ${pacingText}, ${repText}.`;
}

export async function pickSysInt() {
    const id = document.getElementById("sysIntSelect").value;
    let response;
    try {
        response = await getSysInt(id);
        if (response && response.success) {
            const sysInt = response.instruction;
            const updatedSysInt = buildSysIntOptions(sysInt);
            const systemInstructionField = document.getElementById("systeminstruction");
            systemInstructionField.value = updatedSysInt;
            systemInstructionField.dispatchEvent(new Event('input', { bubbles: true }));
        }
    } catch (err) {
        handleAjaxError({err, context: "Get System Instruction"});


    };
}
