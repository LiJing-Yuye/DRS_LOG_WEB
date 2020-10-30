const save_string = function(filename, string) {
    var urlObject = window.URL || window.webkitURL || window
    var export_blob = new Blob([string])
    var save_link = document.createElementNS(
        'http://www.w3.org/1999/xhtml',
        'a'
    )
    save_link.href = urlObject.createObjectURL(export_blob)
    save_link.download = filename

    var ev = document.createEvent('MouseEvents')
    ev.initMouseEvent(
        'click',
        true,
        false,
        window,
        0,
        0,
        0,
        0,
        0,
        false,
        false,
        false,
        false,
        0,
        null
    )
    save_link.dispatchEvent(ev)
}

const filter_json = function(content) {
    if (content.indexOf("b'") == 0) {
        content = content.substring(2)
        content = content.substring(0, content.length - 1)
    }

    content = content.replace(/\\\\n/g, '\\?')
    // content = content.replace(/\\n/g, '\n')
    content = content.replace(/\\\\/g, '\\')
    content = content.replace(/\\\?/g, '\\n')
    content = content.replace(/\\r/g, '')
    content = content.replace(/\\'/g, "'")
    content = content.replace(/\\x/g, '\\\\x')

    return content
}

const filter_xml = function(content) {
    content = content.replace(/\\n/g, '\n')
    content = content.replace(/\\t/g, '\t')
    content = content.replace(/\\'/g, "'")
    content = content.replace(/\\x'/g, '\\\\x')

    content = content.replace(/\\r/g, '')
    if (content.indexOf("b'") == 0) {
        content = content.substring(2)
        content = content.substring(0, content.length - 1)
    }

    return content
}
module.exports = { save_string, filter_json, filter_xml }
