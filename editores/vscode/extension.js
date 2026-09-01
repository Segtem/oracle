// Cliente mínimo del servidor LSP de Oracle, sin dependencias de npm.
//
// El protocolo se habla a mano —cabeceras `Content-Length` y JSON— en vez de usar
// `vscode-languageclient`. El motivo no es purismo: el instalador arma el .vsix con
// Python y zipfile, sin `npm` ni `vsce`, para que el taller siga siendo un solo
// archivo copiable por USB. Traer una dependencia rompería eso.
//
// Y el servidor es el MISMO que usa Emacs: acá no se reimplementa ningún
// diagnóstico. Duplicar la traducción de errores sería el defecto que este
// proyecto persigue.
const vscode = require('vscode');
const { spawn } = require('child_process');
const path = require('path');

let servidor = null, pendientes = new Map(), siguienteId = 1, buffer = Buffer.alloc(0);
let diagnosticos = null, registro = null;
let subrayadoError = null, subrayadoAviso = null;
const porArchivo = new Map();

// Un cliente que no puede decir por qué el servidor no contesta falla en silencio, que
// es lo que este proyecto persigue. Todo lo que el servidor escriba en stderr, y todo
// fallo de arranque, queda registrado.
//
// Va a un ARCHIVO además del panel «Output», y no es redundancia: el perfil de aula
// oculta a propósito las pestañas del panel —`workbench.panel.output` y también
// `workbench.panel.markers`, o sea PROBLEMS— para dejar sólo la terminal, como
// cs50.dev. En esa configuración un canal de Output no lo ve nadie.
const ARCHIVO_REGISTRO = require('path').join(require('os').tmpdir(), 'oracle-vscode.log');

function anotar(texto) {
    const linea = `${new Date().toISOString().slice(11, 19)}  ${texto}`;
    if (registro) registro.appendLine(linea);
    try { require('fs').appendFileSync(ARCHIVO_REGISTRO, linea + '\n'); } catch (e) { /* no importa */ }
}

// El servidor se busca en tres escalones, del más portable al más específico.
//
// Antes era una sola ruta clavada —`~/Dev/oracle/tools/lsp.py`—, que anda en la máquina donde se
// escribió Oracle y en ninguna otra. Con el paquete instalado (`pip install oracle-metalenguaje`)
// el ejecutable `oracle-lsp` queda en el PATH y no hace falta que exista ningún checkout.
//
// `ORACLE_LSP` existe para el caso intermedio: alguien que tiene el repositorio en otro sitio y
// quiere que el editor use ESE y no el instalado, que es lo que uno quiere mientras desarrolla.
function comandoDelServidor() {
    const fs = require('fs');
    const explicito = process.env.ORACLE_LSP;
    if (explicito && fs.existsSync(explicito)) {
        return { cmd: 'python3', args: [explicito], como: `ORACLE_LSP=${explicito}` };
    }
    for (const dir of (process.env.PATH || '').split(path.delimiter)) {
        const cand = path.join(dir, 'oracle-lsp');
        try {
            fs.accessSync(cand, fs.constants.X_OK);
            return { cmd: cand, args: [], como: `oracle-lsp en ${dir}` };
        } catch (e) { /* sigue buscando */ }
    }
    const checkout = path.join(process.env.HOME || '', 'Dev', 'oracle', 'tools', 'lsp.py');
    if (fs.existsSync(checkout)) {
        return { cmd: 'python3', args: [checkout], como: `checkout en ${checkout}` };
    }
    return null;
}

function enviar(mensaje) {
    if (!servidor) return;
    const cuerpo = Buffer.from(JSON.stringify({ jsonrpc: '2.0', ...mensaje }), 'utf8');
    servidor.stdin.write(`Content-Length: ${cuerpo.length}\r\n\r\n`);
    servidor.stdin.write(cuerpo);
}

function pedir(method, params) {
    const id = siguienteId++;
    return new Promise((resolve) => {
        pendientes.set(id, resolve);
        enviar({ id, method, params });
        setTimeout(() => { if (pendientes.delete(id)) resolve(null); }, 5000);
    });
}

// Un mensaje puede llegar partido en varios `data`, y varios mensajes pueden llegar
// juntos en uno solo. Sin este bucle el cliente anda en las pruebas y falla con un
// archivo grande, que es la peor forma de fallar.
function alRecibir(trozo) {
    buffer = Buffer.concat([buffer, trozo]);
    for (;;) {
        const corte = buffer.indexOf('\r\n\r\n');
        if (corte < 0) return;
        const cabeceras = buffer.subarray(0, corte).toString('utf8');
        const largo = /Content-Length: (\d+)/i.exec(cabeceras);
        if (!largo) return;
        const desde = corte + 4, hasta = desde + Number(largo[1]);
        if (buffer.length < hasta) return;
        let mensaje = null;
        try { mensaje = JSON.parse(buffer.subarray(desde, hasta).toString('utf8')); } catch (e) { /* se descarta */ }
        buffer = buffer.subarray(hasta);
        if (!mensaje) continue;
        if (mensaje.id !== undefined && pendientes.has(mensaje.id)) {
            pendientes.get(mensaje.id)(mensaje.result);
            pendientes.delete(mensaje.id);
        } else if (mensaje.method === 'textDocument/publishDiagnostics') {
            publicar(mensaje.params);
        }
    }
}

function publicar(params) {
    if (!diagnosticos) return;
    const crudos = params.diagnostics || [];
    anotar(`diagnósticos para ${params.uri}: ${crudos.length}`);
    const uri = vscode.Uri.parse(params.uri);
    const uri0 = uri.toString();
    const doc = vscode.workspace.textDocuments.find((x) => x.uri.toString() === uri0);
    // El servidor ya garantiza un rango con ancho. Esto es sólo la red: si alguna vez
    // llegara uno vacío —el editor recorta la columna contra el fin de la línea, así
    // que un error señalado al final de una línea produce uno— se subraya la línea
    // entera antes que no dibujar nada.
    const rango = (d) => {
        const ini = new vscode.Position(d.range.start.line, d.range.start.character);
        const fin = new vscode.Position(d.range.end.line, d.range.end.character);
        const pedido = doc ? doc.validateRange(new vscode.Range(ini, fin))
                           : new vscode.Range(ini, fin);
        if (!pedido.isEmpty || !doc) return pedido;
        const linea = doc.lineAt(pedido.start.line);
        return new vscode.Range(linea.lineNumber, linea.firstNonWhitespaceCharacterIndex,
                                linea.lineNumber, linea.range.end.character);
    };
    diagnosticos.set(uri, crudos.map((d) => {
        const diag = new vscode.Diagnostic(rango(d), d.message,
            d.severity === 1 ? vscode.DiagnosticSeverity.Error : vscode.DiagnosticSeverity.Warning);
        diag.source = 'oracle';
        return diag;
    }));
    // Un rango de un carácter es casi invisible. Se estira hasta el fin de la línea,
    // que es lo que hace VS Code con sus propios diagnósticos cuando el rango es vacío.
    porArchivo.set(uri.toString(), crudos.map((d) => ({
        range: rango(d),
        hoverMessage: d.message,
        severidad: d.severity,
    })));
    pintar();
}

// Oracle dibuja SU PROPIO subrayado en vez de confiar en el de VS Code.
//
// El perfil de aula replica cs50.dev, y ese perfil trae `problems.visibility: false`
// —viene del devcontainer.json oficial de CS50, no es un invento de acá—, que apaga
// los subrayados de TODO el editor. Ese ajuste no acepta configuración por lenguaje:
// su definición no declara `scope`, así que vale para la ventana entera.
//
// Cambiarlo globalmente encendería también Pylance y Java, y rompería la paridad con
// cs50.dev que es el motivo de este perfil. Una decoración propia no depende de ese
// ajuste: enciende el subrayado SÓLO para `.oracle` y `.caso`, y deja C, Python y Java
// exactamente como CS50 los configuró.
function anutar_editores(visibles) {
    anotar(`pintar: ${visibles.length} editores visibles · ` + visibles.map(
        (e) => `${e.document.languageId}:${(porArchivo.get(e.document.uri.toString()) || []).length}`).join(', '));
}

function pintar() {
    if (!subrayadoError) return;
    const visibles = vscode.window.visibleTextEditors;
    anutar_editores(visibles);
    for (const editor of visibles) {
        if (editor.document.languageId !== 'oracle') continue;
        const marcas = porArchivo.get(editor.document.uri.toString()) || [];
        editor.setDecorations(subrayadoError, marcas.filter((m) => m.severidad === 1));
        editor.setDecorations(subrayadoAviso, marcas.filter((m) => m.severidad !== 1));
    }
}

function abrir(doc) {
    if (doc.languageId !== 'oracle' || !servidor) return;
    enviar({ method: 'textDocument/didOpen', params: { textDocument: {
        uri: doc.uri.toString(), languageId: 'oracle', version: doc.version, text: doc.getText() } } });
}

function activate(contexto) {
    diagnosticos = vscode.languages.createDiagnosticCollection('oracle');
    registro = vscode.window.createOutputChannel('Oracle');
    // Dos capas a propósito. El subrayado ondulado es lo que se espera ver, pero
    // `textDecoration` es CSS crudo que VS Code puede rechazar entero si algo no le
    // gusta —pasó con `underline wavy #f14c4c 1px`: el grosor invalidaba la
    // declaración y no se dibujaba nada—. El fondo tenue y la marca en la regla
    // lateral no dependen de eso: si el subrayado no sale, el error igual se ve.
    subrayadoError = vscode.window.createTextEditorDecorationType({
        textDecoration: 'underline wavy #f14c4c',
        backgroundColor: 'rgba(241, 76, 76, 0.18)',
        overviewRulerColor: '#f14c4c',
        overviewRulerLane: vscode.OverviewRulerLane.Right,
    });
    subrayadoAviso = vscode.window.createTextEditorDecorationType({
        textDecoration: 'underline wavy #cca700',
        backgroundColor: 'rgba(204, 167, 0, 0.18)',
        overviewRulerColor: '#cca700',
        overviewRulerLane: vscode.OverviewRulerLane.Right,
    });
    contexto.subscriptions.push(diagnosticos, registro, subrayadoError, subrayadoAviso,
        vscode.window.onDidChangeVisibleTextEditors(pintar));

    anotar(`— arranque — registro en ${ARCHIVO_REGISTRO}`);
    const servidorHallado = comandoDelServidor();
    if (!servidorHallado) {
        anotar('no se encontró el servidor. El resaltado funciona; los diagnósticos no.');
        vscode.window.showWarningMessage(
            'Oracle: no se encontró el servidor. Instalá el paquete (`pip install ' +
            'oracle-metalenguaje`), o apuntá ORACLE_LSP al `tools/lsp.py` de tu checkout.');
        return;
    }
    anotar(`arrancando: ${servidorHallado.como}`);
    // El servidor resuelve el proyecto —qué catálogo y qué corpus mirar— desde su directorio
    // de trabajo. Sin pasarlo, hereda el de VS Code: la carpeta abierta si arrancaste con
    // `code <carpeta>`, y `/` si abriste desde el lanzador del escritorio. En ese segundo caso
    // no encuentra `oracle.json` y el aviso «SIN FIJAR» y el lens salen vacíos, sin decir por qué.
    const carpeta = (vscode.workspace.workspaceFolders || [])[0];
    const raiz = carpeta && carpeta.uri.scheme === 'file' ? carpeta.uri.fsPath : undefined;
    anotar(`directorio del proyecto: ${raiz || '(ninguna carpeta abierta)'}`);
    servidor = spawn(servidorHallado.cmd, servidorHallado.args,
                     { cwd: raiz, stdio: ['pipe', 'pipe', 'pipe'] });
    servidor.on('error', (e) => {
        anotar(`no se pudo arrancar: ${e.message}`);
        vscode.window.showWarningMessage(`Oracle: no se pudo iniciar el servidor (${e.message}).`);
        servidor = null;
    });
    servidor.on('exit', (codigo) => anotar(`el servidor terminó con código ${codigo}`));
    servidor.stderr.on('data', (d) => anotar(`stderr: ${d.toString().trimEnd()}`));
    servidor.stdout.on('data', alRecibir);

    enviar({ id: siguienteId++, method: 'initialize', params: {
        processId: process.pid,
        rootUri: vscode.workspace.workspaceFolders?.[0]?.uri.toString() ?? null,
        capabilities: {} } });
    enviar({ method: 'initialized', params: {} });

    contexto.subscriptions.push(
        vscode.workspace.onDidOpenTextDocument(abrir),
        vscode.workspace.onDidSaveTextDocument(abrir),
        vscode.workspace.onDidChangeTextDocument((e) => abrir(e.document)));
    vscode.workspace.textDocuments.forEach(abrir);

    contexto.subscriptions.push(vscode.languages.registerCompletionItemProvider('oracle', {
        async provideCompletionItems(doc, pos) {
            abrir(doc);
            const r = await pedir('textDocument/completion', {
                textDocument: { uri: doc.uri.toString() },
                position: { line: pos.line, character: pos.character } });
            const items = Array.isArray(r) ? r : (r && r.items) || [];
            return items.map((i) => {
                const it = new vscode.CompletionItem(i.label, vscode.CompletionItemKind.Field);
                // `detail` es donde viaja la UNIDAD del campo: `flotante · cm`. Es lo que ningún
                // otro editor muestra, y la razón de que este completado valga la pena.
                if (i.detail) it.detail = i.detail;
                if (i.documentation) it.documentation = i.documentation;
                return it;
            });
        }
    }, '.', ' '));

    // El lens es la misma línea que imprime `python tools/medida.py --listar`, arriba de la
    // medida: qué la pone a prueba y con qué umbral. La arma el servidor, no este archivo —si el
    // cliente contara casos por su cuenta volveríamos a tener dos definiciones de «ejercitada»,
    // que es justo el defecto que este lens existe para hacer visible.
    //
    // Sin `command` el lens no es clicable, y está bien: informa, no ejecuta nada.
    contexto.subscriptions.push(vscode.languages.registerCodeLensProvider('oracle', {
        async provideCodeLenses(doc) {
            abrir(doc);
            const r = await pedir('textDocument/codeLens', {
                textDocument: { uri: doc.uri.toString() } });
            if (!Array.isArray(r)) return [];
            return r.map((l) => new vscode.CodeLens(
                new vscode.Range(l.range.start.line, l.range.start.character,
                                 l.range.end.line, l.range.end.character),
                { title: l.command.title, command: '' }));
        }
    }));
}

function deactivate() { if (servidor) servidor.kill(); }

module.exports = { activate, deactivate };
