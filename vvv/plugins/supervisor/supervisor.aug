module Supervisor =

let comment = 
    IniFile.comment /[#;]/ "#"

let title_comment = 
    [ label "#titlecomment" . del /[ \t]*[#;][ \t]*/ " # " . store /[^ \t\r\n]([^\r\n]*[^ \t\r\n])?/ ]

let title_noeol (kw:regexp)
    = Util.del_str "[" . key kw . Util.del_str "]" . title_comment? . Util.doseol


let indented_title_noeol (kw:regexp)
   = Util.indent . title_noeol kw


let sep        = IniFile.sep "=" "="
let entry      = IniFile.indented_entry IniFile.entry_re sep comment
let title      = indented_title_noeol IniFile.record_re
let record     = IniFile.record title entry
let lns        = IniFile.lns record comment
let filter = (incl "/etc/supervisor/supervisord.conf") . Util.stdexcl
let xfm = transform lns filter
