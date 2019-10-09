# jbb
Jenkins + Bitbucket stash scripts

if anyone would find this useful - feel free to use!

_clean_all.py_ - deletes ALL jobs, folders and views from Jenkins

_clean_view.py_ - deletes ALL jobs and folders from a view, and after that deletes the view

_view_export.py_ - allows to select a view and creates a full dump of ordered(!) folders and jobs structure of that view locally (in "imports" subfolder)

_view_import.py_ - imports the structure of all(!) views in subfolder "imports" to Jenkins (creates views, folders and jobs)

_main.py_ - allows to view, create from template and delete Jenkins jobs/folders and also allows to view, create or delete a PR notification in Bitbucket repositories.

__The code is not ideal at all, it was written just to work  Feel free to improve it!__
