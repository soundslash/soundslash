
import datetime
import time
import math
import os


debug = True

tmpl_cache = {}
def tmpl(handler, filename):
    if not debug and filename in tmpl_cache:
        return tmpl_cache[filename]
    else:
        with open(os.getcwd()+"/src/web/static/js/tpl/"+filename, "r") as file:
            tmpl_cache[filename] = file.read()
        return tmpl_cache[filename]
def tmpl2(handler, id, filename):
    return """<script id=\""""+id+"""\" type="text/x-tmpl">"""+"\n"+tmpl(handler, filename)+"\n"+"""</script>"""

def now_uniq(handler):
    now = datetime.datetime.now()
    return str(time.mktime(now.timetuple())*1e3 + now.microsecond/1e3 * 1000)

def equals(handler, variable, equals):
    globals = handler.template_vars
    if str(variable) in globals and globals[str(variable)] == equals:
        return True
    else:
        return False

def var(handler, variable, subvariable=None):
    globals = handler.template_vars
    if str(variable) in globals:
        if subvariable is not None:
            if str(subvariable) in globals[str(variable)]:
                return globals[str(variable)][str(subvariable)]
            else:
                return ""
        return globals[str(variable)]
    else:
        return ""

def to_secs(handler, number):
    return round(float(number)/float(1000000000), 2)

def format_secs(handler, seconds):
    mins = int(math.floor(seconds/60))
    secs = int(math.ceil(seconds%60))
    # microsecs = int(((seconds%60)*1000)%1000)
    return str(mins)+":"+str(secs)

def to_mb(handler, number):
    return round(float(number)/1048576, 2)