;;; Utils for building BattMo doc

;; Use user-login-name to get user name
;; (cond '(compare-strings user-login-name "xavier")

(pcase (user-login-name)
  ("xavier"  (setq docdir "/home/xavier/Python/domain-electrochemistry/sphinx/")
   ))

(defun battinfodoc-local-open ()
  "Open locally built documentation in browser"
  (interactive)
  (browse-url (concat docdir "_build/html/index.html"))
  )


(defun battinfodoc-build ()
  "Build BattMo documentation"
  (interactive)
  (let* (
         (outputbuffer (get-buffer-create "*buildoutput*"))
         )
    (delete-directory (concat docdir "_build") t)
    (pop-to-buffer outputbuffer)
    ;; (pyvenv-activate "~/Python/battinfo-doc-3.12-env/")
    (pyvenv-activate "/home/xavier/Python/battinfodoc.env")
    (cd docdir)
    (erase-buffer)
    (start-process "battinfo-build" outputbuffer "make" "html")
    )
  )

