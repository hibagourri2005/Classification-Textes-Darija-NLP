// ==UserScript==
// @name         Gemini Batch Darija NER (Text Injection) - Tab Mode V9.0 FIXED
// @namespace    http://tampermonkey.net/
// @version      9.0
// @description  Automates Moroccan Darija NER tagging. FIXED: File content is read before IndexedDB storage.
// @author       You
// @match        https://gemini.google.com/u/0/*
// @grant        GM_openInTab
// ==/UserScript==

(function() {
    'use strict';

    const CONFIG = {
        targetUrl: "https://gemini.google.com/u/0/",
        dbName: "Gemini_NER_V9",
        storeName: "file_queue",
        networkSafetyDelay: 8000
    };

    const BASE_PROMPT = `Tu es un expert en linguistique marocaine spécialisé dans l'annotation de textes en Darija
(arabe dialectal marocain, Darija écrit en alphabet arabe, latin ou Arabizi).

Ta tâche est de classifier des commentaires YouTube marocains dans exactement 12 classes thématiques.

Le Darija est une langue à faibles ressources et peut apparaître sous plusieurs formes :

- alphabet arabe
- alphabet latin
- Arabizi (ex : 3 = ع, 7 = ح, 9 = ق, 5 = خ, 8 = ه, 2 = ء)

Les commentaires peuvent aussi contenir du français, de l'arabe standard ou de l'anglais mélangés.
Tu dois comprendre et classifier le contenu dans n'importe laquelle de ces langues ou mélanges.
Un texte en Arabizi comme "3ndek shi wa7" n'est pas "inclassable" — c'est une "question_general".

---

RÈGLE CRITIQUE

La classification doit se baser UNIQUEMENT sur le contenu du commentaire.

IGNORER COMPLÈTEMENT toute information externe comme :

- domain
- channel_name
- source_type
- language
- script

Ces champs décrivent la chaîne YouTube et NON le contenu réel du commentaire.

Même si une chaîne parle de sport ou de religion,
un commentaire peut appartenir à n'importe quelle classe.

---

RÈGLES ABSOLUES

1. Retourner UNIQUEMENT un objet JSON valide.
2. Aucun texte avant ou après le JSON.
3. Chaque clé correspond à l'index du texte ("0", "1", "2"...).
4. Chaque valeur doit être exactement un des 12 labels ci-dessous.
5. Ne jamais inventer de label.
6. Ne jamais laisser un champ vide.
7. Labels en minuscules sans accent :
   food, entertainment, politics, business, medical, sports, religion, soutien, inclassable, question_general, opinion, publicite.
8. Si plusieurs classes → choisir la dominante.
9. Un texte Arabizi n'est jamais inclassable sauf absence de sens.

---

LES 12 CLASSES

01 | food
Cuisine, recettes, ingrédients
Mots : recette, cuisine, طبخ, ماكلة, وصفة, طاجين, cook

02 | entertainment
Humour, vidéos, fun
Mots : hhh, lol, mdrrrr, funny, 😂

03 | politics
Politique, société
Mots : حكومة, بلاد, maroc, prix, election

04 | business
Commerce, argent
Mots : business, dropshipping, formation, فلوس

05 | medical
Santé
Mots : مرض, دواء, طبيب, douleur, pharmacie

06 | sports
Sport, football
Mots : match, raja, wydad, goal

07 | religion
Religion islam
Mots : صلاة, قرآن, حلال, حرام
⚠️ invocation à une personne vivante → soutien

08 | soutien
Encouragement
Mots : bravo, merci, الله يعطيك الصحة

09 | inclassable
Pas de sens exploitable
Ex : 😂😂😂 / salam / ...

10 | question_general
Question générale
Mots : wach, kifach, pourquoi

11 | opinion
Avis personnel
Mots : ma 3jbatnich, kndhon

12 | publicite
Promotion
Mots : subscribe, contact, WhatsApp

---

RÈGLES CAS LIMITES

- Remerciement + question → question
- Invocation vivante → soutien
- Invocation mort → religion
- Question spécifique → domaine
- Emojis seuls → inclassable
- Moins de 3 mots sans sens → inclassable
- Avis → opinion
- Promotion → publicite
- Arabizi compréhensible → classer normalement

---

FORMAT DE SORTIE OBLIGATOIRE

Retourner UNIQUEMENT un tableau JSON valide.

Chaque élément doit contenir EXACTEMENT ces 3 champs :

- "id" : repris EXACTEMENT depuis l'entrée
- "text" : valeur de "text_normalized" (copiée sans modification)
- "label" : un des 12 labels

Structure :

[
  {
    "id": "darija_050244",
    "text": "واش ملي نعمروهم في البواطة نعمل في الكنجلاطور كتبقا مزيانة",
    "label": "food"
  }
]

RÈGLES STRICTES :

- Lire le champ "text_normalized" et le renommer en "text"
- Ne jamais utiliser "text_normalized" dans la sortie
- Copier exactement "id" sans modification
- Ignorer complètement "domain" et "label" d'entrée
- Ne jamais changer l'ordre
- Aucun texte hors JSON
---


TEXTES À CLASSIFIER

Classifier les commentaires suivants.
Retourner uniquement le JSON.


`;

    // --- DATABASE LOGIC ---
    // FIX: Files are now stored as plain text strings, not File objects.
    // File objects are not serializable by IndexedDB and become empty after retrieval.
    const DB = {
        open: () => new Promise((resolve, reject) => {
            const r = indexedDB.open(CONFIG.dbName, 1);
            r.onupgradeneeded = e => e.target.result.createObjectStore(CONFIG.storeName, { keyPath: "id", autoIncrement: true });
            r.onsuccess = e => resolve(e.target.result);
            r.onerror = e => reject(e);
        }),

        // FIX: Read ALL file contents first, THEN open one transaction to store them all.
        // Doing await inside a transaction kills it (TransactionInactiveError).
        addFiles: async (files) => {
            // Step 1: Read all files OUTSIDE the transaction (await is safe here)
            const records = [];
            for (let f of files) {
                const content = await f.text();
                records.push({ name: f.name, content: content, status: "pending", added: Date.now() });
            }

            // Step 2: Open transaction AFTER all reads are done — no await inside
            const db = await DB.open();
            const tx = db.transaction(CONFIG.storeName, "readwrite");
            const store = tx.objectStore(CONFIG.storeName);
            for (let record of records) {
                store.add(record);  // Synchronous — transaction stays alive
            }
            return new Promise(r => tx.oncomplete = r);
        },

        getNext: async () => {
            const db = await DB.open();
            return new Promise(resolve => {
                const tx = db.transaction(CONFIG.storeName, "readonly");
                const store = tx.objectStore(CONFIG.storeName);
                const req = store.openCursor();
                req.onsuccess = e => {
                    const c = e.target.result;
                    if (c && c.value.status === "pending") resolve(c.value);
                    else if (c) c.continue();
                    else resolve(null);
                };
            });
        },

        markDone: async (id) => {
            const db = await DB.open();
            const tx = db.transaction(CONFIG.storeName, "readwrite");
            const store = tx.objectStore(CONFIG.storeName);
            const r = store.get(id);
            r.onsuccess = () => { r.result.status = "done"; store.put(r.result); };
            return new Promise(r => tx.oncomplete = r);
        },

        count: async () => {
            const db = await DB.open();
            return new Promise(r => {
                const tx = db.transaction(CONFIG.storeName, "readonly");
                const req = tx.objectStore(CONFIG.storeName).getAll();
                req.onsuccess = () => r(req.result.filter(i => i.status === "pending").length);
            });
        },

        clearAll: async () => {
            const db = await DB.open();
            const tx = db.transaction(CONFIG.storeName, "readwrite");
            tx.objectStore(CONFIG.storeName).clear();
            return new Promise(r => tx.oncomplete = r);
        }
    };


    // Intercepter les erreurs réseau Gemini
    const originalFetch = window.fetch;
    window.fetch = async (...args) => {
        try {
            const response = await originalFetch(...args);
            if (!response.ok) {
                console.error(`🔴 Fetch Error: ${response.status} ${response.statusText}`, args[0]);
            }
            return response;
        } catch (err) {
            console.error('🔴 Fetch Failed:', err, args[0]);
            throw err;
        }
    };

    window.addEventListener('unhandledrejection', event => {
        console.error('🔴 Unhandled Promise Rejection:', event.reason);
    });



    // --- AUTOMATION LOOP ---
    async function runLoop() {
        if (localStorage.getItem("LoopActive") !== "true") return;

        const fileData = await DB.getNext();
        if (!fileData) {
            localStorage.setItem("LoopActive", "false");
            alert("✅ Batch Complete.");
            return;
        }

        updateOverlay(`Processing: ${fileData.name}`);

        const textContent = fileData.content;

        if (!textContent || textContent.trim() === "") {
            console.error("Empty content for file:", fileData.name);
            updateOverlay(`❌ Empty content: ${fileData.name}`);
            await delay(2000);
            await DB.markDone(fileData.id);
            runLoop();
            return;
        }

        // Cliquer sur "New chat" pour ouvrir une nouvelle conversation
        const newChatBtn = document.querySelector('a[href*="new"], button[aria-label*="new" i], [data-test-id="new-chat"]')
        || Array.from(document.querySelectorAll('a, button')).find(el => el.innerText.trim().toLowerCase().includes('new chat'));

        if (newChatBtn) {
            newChatBtn.click();
            updateOverlay(`🆕 New chat opened...`);
        } else {
            // fallback : aller directement sur l'URL
            window.location.href = CONFIG.targetUrl;
            return;
        }

        // Attendre que le nouvel éditeur soit prêt
        let editor = null;
        for (let i = 0; i < 40; i++) {
            editor = document.querySelector('.ql-editor.textarea') || document.querySelector('.ql-editor');
            if (editor && editor.isConnected) break;
            await delay(1000);
        }

        if (!editor) {
            updateOverlay(`❌ Editor not found, retrying...`);
            await delay(3000);
            window.location.reload();
            return;
        }

        await delay(2000);
        editor.focus();
        await delay(500);

        const finalPrompt = `[SOURCE:${fileData.name}]\n` + BASE_PROMPT + textContent;
        document.execCommand('insertText', false, finalPrompt);
        editor.dispatchEvent(new Event('input', { bubbles: true }));

        await delay(2000);

        // Attendre que le bouton soit actif et cliquer
        let sent = false;
        for (let i = 0; i < 60; i++) {
            const btn = document.querySelector('.send-button');
            const container = document.querySelector('.send-button-container');
            if (btn && container && !container.classList.contains('disabled')) {
                await delay(300);
                btn.click();
                sent = true;
                break;
            }
            await delay(1000);
        }

        if (sent) {
            updateOverlay(`⏳ Waiting for Gemini response...`);
            // Attendre que Gemini finisse de répondre
            await delay(5000);

            // Attendre que le bouton stop disparaisse (réponse terminée)
            for (let i = 0; i < 60; i++) {
                const stopBtn = document.querySelector('.stop-button, [aria-label*="stop" i]');
                if (!stopBtn) break;
                await delay(2000);
            }

            await delay(3000);
            await DB.markDone(fileData.id);
            updateOverlay(`✅ Done: ${fileData.name}`);
            await delay(2000);
            runLoop(); // appel récursif — même page, pas de nouvelle fenêtre
        } else {
            updateOverlay(`⚠️ Send failed, retrying in 15s...`);
            await delay(15000);
            window.location.reload();
        }
    }

    function delay(ms) { return new Promise(r => setTimeout(r, ms)); }

    function updateOverlay(msg) {
        const el = document.getElementById('status-msg');
        if (el) el.innerText = msg;
    }

    // --- UI ---
    function createUI() {
        if (document.getElementById('batch-panel')) return;
        if (!document.body) { setTimeout(createUI, 500); return; }

        const panel = document.createElement('div');
        panel.id = "batch-panel";
        Object.assign(panel.style, {
            position: 'fixed', top: '80px', right: '20px', zIndex: '2147483647',
            background: '#1e1e1e', color: '#fff', padding: '15px', borderRadius: '12px',
            width: '240px', border: '2px solid #8ab4f8', fontSize: '13px',
            boxShadow: '0 4px 15px rgba(0,0,0,0.5)', fontFamily: 'sans-serif'
        });

        const header = document.createElement('div');
        header.style.cssText = "display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;";
        const title = document.createElement('h3');
        title.innerText = "⚡ NER Batcher V9.0";
        title.style.cssText = "margin:0; color:#8ab4f8; font-size:14px;";
        const closeBtn = document.createElement('span');
        closeBtn.innerText = "✕";
        closeBtn.style.cursor = "pointer";
        closeBtn.onclick = () => panel.style.display = 'none';
        header.appendChild(title);
        header.appendChild(closeBtn);
        panel.appendChild(header);

        const status = document.createElement('div');
        status.id = "status-msg";
        status.innerText = "Checking DB...";
        status.style.cssText = "margin-bottom:10px; background:#333; padding:5px; border-radius:4px; text-align:center;";
        panel.appendChild(status);

        const fileInput = document.createElement('input');
        fileInput.type = "file";
        fileInput.id = "files";
        fileInput.multiple = true;
        fileInput.style.cssText = "width:100%; margin-bottom:10px; font-size:11px;";
        panel.appendChild(fileInput);

        const btnLoad = document.createElement('button');
        btnLoad.innerText = "1. Load Files";
        btnLoad.style.cssText = "width:100%; padding:8px; margin-bottom:8px; cursor:pointer; border-radius:4px; border:none; background:#444; color:white;";
        btnLoad.onclick = async () => {
            const f = fileInput.files;
            if (f.length) {
                btnLoad.innerText = "Loading...";
                btnLoad.disabled = true;
                await DB.addFiles(Array.from(f));
                const count = await DB.count();
                updateOverlay(`✅ Queued ${f.length} files. Total: ${count}`);
                btnLoad.innerText = "1. Load Files";
                btnLoad.disabled = false;
            }
        };
        panel.appendChild(btnLoad);

        const btnStart = document.createElement('button');
        btnStart.innerText = "2. START BATCH";
        btnStart.style.cssText = "width:100%; padding:12px; background:#8ab4f8; color:black; font-weight:bold; cursor:pointer; border-radius:4px; border:none;";
        btnStart.onclick = () => {
            localStorage.setItem("LoopActive", "true");
            runLoop();
        };
        panel.appendChild(btnStart);

        const btnStop = document.createElement('button');
        btnStop.innerText = "STOP / RESET";
        btnStop.style.cssText = "width:100%; padding:8px; margin-top:8px; background:#ff4641; color:white; cursor:pointer; border-radius:4px; border:none; font-size:11px;";
        btnStop.onclick = () => {
            localStorage.setItem("LoopActive", "false");
            window.location.reload();
        };
        panel.appendChild(btnStop);

        const btnClear = document.createElement('button');
        btnClear.innerText = "🗑️ Clear Database";
        btnClear.style.cssText = "width:100%; padding:8px; margin-top:8px; background:#fbbc04; color:black; font-weight:bold; cursor:pointer; border-radius:4px; border:none; font-size:11px;";
        btnClear.onclick = async () => {
            if (confirm("Clear all queued files? This cannot be undone.")) {
                await DB.clearAll();
                fileInput.value = "";
                updateOverlay("🗑️ Database Cleared.");
            }
        };
        panel.appendChild(btnClear);

        document.body.appendChild(panel);
        DB.count().then(c => updateOverlay(`${c} files pending.`));
    }

    function init() {
        if (document.body) createUI();
        else setTimeout(init, 500);
    }

    init();

    if (localStorage.getItem("LoopActive") === "true") {
        setTimeout(runLoop, 4000);
    }
})();