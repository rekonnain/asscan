function createurl(host, port) {
    let scheme = ''
    if (port == 80 || (port >= 8080 && port <= 8090) || (port >= 8888 && port <= 8890) || port == 3128) {
        scheme = 'http'
    } else if (port == 443 || port == 8443) {
        scheme = 'https'
    } else if (port == 3389) {
        return 'rdp://' + host
    } else if (port >= 5900 && port <= 5910) {
        return 'vnc://' + host + '::' + port
    } else if (port == 445) {
        return 'smb://' + host
    } else if (port == 21) {
        scheme = 'ftp'
    } else if (port == 23) {
        return 'telnet://' + host
    } else if (port == 22) {
        return 'ssh://' + host
    }
    if (scheme.length > 0) {
        return scheme + '://' + host + ':' + port
    } else {
        return ''
    }
}

module.exports = {
    createurl: createurl
}