module.exports = async function(context, commands) {
    let url = context.options.browsertime.url;
    let reloads = context.options.browsertime.reloads;
    await commands.measure.start(url, 'cold load');

    // According to the docs you need to prepend a dummy parameter to test the same page in browsertime:
    // https://www.sitespeed.io/documentation/sitespeed.io/scripting/
    let dummy = url.indexOf('?') == -1 ? '/?dummy' : '&dummy';
    for(count = 0; count < reloads; count++) {
        await commands.wait.byTime(3000)
        await commands.measure.start(url + dummy + count, 'reload' + count);
    }
    return true;
};
