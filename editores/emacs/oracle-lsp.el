;;; oracle-lsp.el --- Oracle en emacs50 -*- lexical-binding: t; -*-

;; Cliente para el servidor LSP de Oracle (ver `oracle-lsp--comando` más abajo):
;; diagnósticos y completado. El completado muestra la UNIDAD de cada campo, y
;; se calla dentro de `porque` y `alcance` a propósito: esa decisión es del
;; humano, no del editor.

;;; Code:

;; Modo mayor mínimo: Oracle es indentación de 4 espacios y nada más.
(define-derived-mode oracle-mode prog-mode "Oracle"
  "Modo para medidas (.oracle) y casos (.caso) de Oracle."
  (setq-local indent-tabs-mode nil)
  (setq-local tab-width 4)
  (setq-local comment-start "# "))

(add-to-list 'auto-mode-alist '("\\.oracle\\'" . oracle-mode))
(add-to-list 'auto-mode-alist '("\\.caso\\'"   . oracle-mode))

;; `lsp-mode` RECIBE los diagnósticos pero no los dibuja: necesita un backend.
;; emacs50 no trae flycheck, y sin backend el servidor manda los errores y en la
;; pantalla no pasa nada —comprobado el 2026-09-01—. `flymake` viene con Emacs
;; desde hace años, así que alcanza con pedirlo: cero dependencias nuevas, que es
;; la misma restricción que tiene el núcleo de Oracle.
(setq lsp-diagnostics-provider :flymake)

;; El servidor se busca en tres escalones, del más portable al más específico.
;;
;; Antes era una sola ruta clavada —`~/Dev/oracle/tools/lsp.py`—, que anda en la máquina
;; donde se escribió Oracle y en ninguna otra. Con el paquete instalado (`pip install
;; oracle-metalenguaje`) el ejecutable `oracle-lsp` queda en el PATH y no hace falta que
;; exista ningún checkout. `ORACLE_LSP` cubre el caso intermedio: alguien con el
;; repositorio en otro sitio que quiere que el editor use ESE, que es lo que uno quiere
;; mientras desarrolla.
(defun oracle-lsp--comando ()
  "Cómo arrancar el servidor de Oracle: ORACLE_LSP, luego `oracle-lsp', luego el checkout."
  (let ((explicito (getenv "ORACLE_LSP"))
        (checkout (expand-file-name "~/Dev/oracle/tools/lsp.py")))
    (cond
     ((and explicito (file-exists-p explicito)) (list "python3" explicito))
     ((executable-find "oracle-lsp") (list (executable-find "oracle-lsp")))
     ((file-exists-p checkout) (list "python3" checkout))
     (t (user-error (concat "Oracle: no se encontró el servidor. Instalá el paquete "
                            "(pip install oracle-metalenguaje) o apuntá ORACLE_LSP "
                            "al tools/lsp.py de tu checkout"))))))

(with-eval-after-load 'lsp-mode
  (add-to-list 'lsp-language-id-configuration '(oracle-mode . "oracle"))
  (lsp-register-client
   (make-lsp-client
    :new-connection (lsp-stdio-connection #'oracle-lsp--comando)
    :activation-fn (lsp-activate-on "oracle")
    :server-id 'oracle-lsp))
  ;; La raíz del proyecto es donde vive `oracle.json`: sin eso el servidor no sabe
  ;; qué catálogo ni qué corpus mirar, y el aviso «SIN FIJAR» no sale. Ojo:
  ;; `:root-uri-fn` NO existe en lsp-mode; la forma soportada es enseñarle el
  ;; marcador a `project.el`.
  (with-eval-after-load 'project
    (add-hook 'project-find-functions
              (lambda (dir)
                (when-let ((raiz (locate-dominating-file dir "oracle.json")))
                  (cons 'transient raiz))))))

;; El hook se protege: en un Emacs sin `lsp-mode` —o en batch— abrir un `.oracle`
;; no debe fallar. Sin esta guarda, `emacs -Q -l oracle-lsp.el` revienta con
;; `void-function lsp-deferred` al abrir el primer archivo.
(add-hook 'oracle-mode-hook
          (lambda ()
            (flymake-mode 1)
            ;; `lsp` y no `lsp-deferred`: el diferido espera a que el buffer se
            ;; vuelva visible, y esa condición no se puede comprobar sin una
            ;; ventana de verdad. En una herramienta de aula conviene el arranque
            ;; directo —un archivo se abre un pelo más lento y el servidor está—
            ;; antes que un modo de falla que nadie puede reproducir.
            (when (fboundp 'lsp) (lsp))))

(provide 'oracle-lsp)
;;; oracle-lsp.el ends here
