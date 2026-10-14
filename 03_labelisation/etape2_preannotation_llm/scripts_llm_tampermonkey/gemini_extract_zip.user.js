// ==UserScript==
// @name         Gemini Sidebar Extractor to ZIP (With Stop Button)
// @namespace    http://tampermonkey.net/
// @version      1.3
// @description  Extracts Gemini responses, with the ability to stop midway and download what has been extracted so far.
// @match        https://gemini.google.com/u/3/*
// @require      https://cdnjs.cloudflare.com/ajax/libs/jszip/3.10.1/jszip.min.js
// @grant        none
// ==/UserScript==

/* global JSZip */

(function() {
    'use strict';

    // State variables to control the extraction loop
    let isExtracting = false;
    let cancelRequested = false;

    // 1. Create a floating extraction button
    const btn = document.createElement('button');
    btn.innerText = 'Extract to ZIP';
    btn.style.position = 'fixed';
    btn.style.bottom = '20px';
    btn.style.right = '20px';
    btn.style.zIndex = '9999';
    btn.style.padding = '12px 20px';
    btn.style.backgroundColor = '#1a73e8'; // Google Blue
    btn.style.color = 'white';
    btn.style.border = 'none';
    btn.style.borderRadius = '8px';
    btn.style.cursor = 'pointer';
    btn.style.boxShadow = '0 4px 6px rgba(0,0,0,0.3)';
    btn.style.fontWeight = 'bold';
    btn.style.fontFamily = 'Arial, sans-serif';

    document.body.appendChild(btn);

    // 2. Main Extraction Logic
    btn.addEventListener('click', async () => {
        // If already extracting, treat this click as a "STOP" command
        if (isExtracting) {
            cancelRequested = true;
            btn.innerText = 'Stopping & Saving...';
            btn.disabled = true; // Prevent spam clicking while it wraps up
            btn.style.backgroundColor = '#5f6368'; // Grey
            return;
        }

        // Start extraction process
        isExtracting = true;
        cancelRequested = false;
        btn.innerText = 'Stop & Save ZIP';
        btn.style.backgroundColor = '#ea4335'; // Google Red to indicate "Stop"

        // Initialize JSZip
        const zip = new JSZip();

        // Find all chat links in the sidebar
        const chatLinks = document.querySelectorAll('a.conversation');

        if (chatLinks.length === 0) {
            alert("No sidebar chats found. Please make sure the sidebar is open.");
            resetButton();
            return;
        }

        // 3. Loop through each link
        for (let i = 0; i < chatLinks.length; i++) {
            // Check if the user clicked "Stop"
            if (cancelRequested) {
                console.log("Extraction stopped by user.");
                break; // Exit the loop immediately
            }

            const link = chatLinks[i];


            link.click();

            await new Promise(resolve => setTimeout(resolve, 3500));

            // Récupérer toutes les réponses visibles
            const allAiResponses = document.querySelectorAll('message-content .markdown-main-panel');
            const aiResponses = Array.from(allAiResponses).filter(el => {
                const rect = el.getBoundingClientRect();
                return rect.width > 0 && rect.height > 0;
            });

            // Chercher le SOURCE dans le message utilisateur
            const userQueryEl = document.querySelector('div[id^="user-query-content-"].query-content');
            const sourceMatch = userQueryEl?.innerText.match(/\[SOURCE:(.+?)\]/);
            let rawTitle = sourceMatch ? sourceMatch[1].replace('.json', '') : `Chat_${i + 1}`;
            let filename = `${rawTitle}.json`;
            // Extraire le JSON
            let jsonContent = "";
            if (aiResponses.length === 0) {
                jsonContent = "[]";
            } else {
                const lastResponse = aiResponses[aiResponses.length - 1].innerText.trim();
                jsonContent = lastResponse
                    .replace(/^```json\s*/i, '')
                    .replace(/^```\s*/i, '')
                    .replace(/```$/i, '')
                    .trim();
            }

            zip.file(filename, jsonContent);
        }

        // 4. Generate and download the ZIP file (only if files exist)
        if (Object.keys(zip.files).length === 0) {
            alert("Extraction stopped before any chats could be saved.");
            resetButton();
            return;
        }

        btn.innerText = 'Zipping files...';

        zip.generateAsync({ type: "blob" }).then(function(content) {
            const link = document.createElement('a');
            link.href = URL.createObjectURL(content);
            link.download = "Gemini_Chats_Export.zip";
            link.style.visibility = 'hidden';
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);

            resetButton();
        });
    });

    // Helper: Reset button state
    function resetButton() {
        isExtracting = false;
        cancelRequested = false;
        btn.disabled = false;
        btn.innerText = 'Extract to ZIP';
        btn.style.backgroundColor = '#1a73e8'; // Back to Google Blue
    }
})();