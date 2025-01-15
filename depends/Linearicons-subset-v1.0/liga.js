/* A polyfill for browsers that don't support ligatures. */
/* The script tag referring to this file must be placed before the ending body tag. */

/* To provide support for elements dynamically added, this script adds
   method 'icomoonLiga' to the window object. You can pass element references to this method.
*/
(function () {
    'use strict';
    function supportsProperty(p) {
        var prefixes = ['Webkit', 'Moz', 'O', 'ms'],
            i,
            div = document.createElement('div'),
            ret = p in div.style;
        if (!ret) {
            p = p.charAt(0).toUpperCase() + p.substr(1);
            for (i = 0; i < prefixes.length; i += 1) {
                ret = prefixes[i] + p in div.style;
                if (ret) {
                    break;
                }
            }
        }
        return ret;
    }
    var icons;
    if (!supportsProperty('fontFeatureSettings')) {
        icons = {
            'network': '&#xe886;',
            'globe2': '&#xe886;',
            'key': '&#xe66e;',
            'unlock2': '&#xe66e;',
            'file-lock': '&#xe6b6;',
            'file4': '&#xe6b6;',
            'envelope': '&#xe696;',
            'mail2': '&#xe696;',
            'user': '&#xe71e;',
            'persona': '&#xe71e;',
            'clock3': '&#xe8e8;',
            'time3': '&#xe8e8;',
            'calendar-empty': '&#xe785;',
            'calendar': '&#xe785;',
            'calendar-31': '&#xe788;',
            'calendar4': '&#xe788;',
            'calendar-full': '&#xe789;',
            'calendar5': '&#xe789;',
            'bookmark2': '&#xe716;',
            'ribbon': '&#xe716;',
            'launch': '&#xe7b0;',
            'share': '&#xe7b0;',
            'share3': '&#xe920;',
            'social': '&#xe920;',
            'satellite2': '&#xe8ca;',
            'antenna2': '&#xe8ca;',
            'magnifier': '&#xe922;',
            'search': '&#xe922;',
            'sun-small': '&#xe646;',
            'brightness': '&#xe646;',
            'moon': '&#xe649;',
            'night': '&#xe649;',
            'cog': '&#xe672;',
            'gear': '&#xe672;',
            'hdd-down': '&#xe6ac;',
            'hdd2': '&#xe6ac;',
            'hdd-up': '&#xe6ad;',
            'hdd3': '&#xe6ad;',
            'download2': '&#xe8f5;',
            'down2': '&#xe8f5;',
            'upload2': '&#xe901;',
            'up2': '&#xe901;',
            'chevron-up': '&#xe902;',
            'up7': '&#xe902;',
            'chevron-down': '&#xe903;',
            'down7': '&#xe903;',
            'chevron-left': '&#xe93b;',
            'left8': '&#xe93b;',
            'chevron-right': '&#xe93c;',
            'right6': '&#xe93c;',
            'chevron-up-circle': '&#xe904;',
            'up12': '&#xe904;',
            'chevron-down-circle': '&#xe905;',
            'down10': '&#xe905;',
            'chevron-left-circle': '&#xe964;',
            'left12': '&#xe964;',
            'chevron-right-circle': '&#xe965;',
            'right9': '&#xe965;',
            'ellipsis': '&#xe9e9;',
            'dots': '&#xe9e9;',
            'equalizer': '&#xe6f2;',
            'settings': '&#xe6f2;',
            'menu': '&#xe92b;',
            'options': '&#xe92b;',
            'cross': '&#xe92a;',
            'cancel': '&#xe92a;',
            'box': '&#xe69f;',
            'storage2': '&#xe69f;',
            'drawers3': '&#xe6a4;',
            'drawer8': '&#xe6a4;',
            'library2': '&#xe718;',
            'book5': '&#xe718;',
            'earth': '&#xe884;',
            'globe': '&#xe884;',
            'enter-down': '&#xe8f8;',
            'down3': '&#xe8f8;',
            'pushpin': '&#xe778;',
            'pin': '&#xe778;',
            'pushpin2': '&#xe779;',
            'pin2': '&#xe779;',
            'map-marker': '&#xe77a;',
            'pin3': '&#xe77a;',
            'tag': '&#xe755;',
            'price4': '&#xe755;',
            'tags': '&#xe756;',
            'price5': '&#xe756;',
            'pictures': '&#xe711;',
            'photo8': '&#xe711;',
            'camera2': '&#xe704;',
            'photo2': '&#xe704;',
            'shutter': '&#xe708;',
            'camera3': '&#xe708;',
            'flare': '&#xe70b;',
            'time-lapse2': '&#xe707;',
            'photo4': '&#xe707;',
            'film2': '&#xe6fc;',
            'photo': '&#xe6fc;',
            'power': '&#xe7bb;',
            'lightning': '&#xe7bb;',
            'power-crossed': '&#xe7bc;',
            'lightning2': '&#xe7bc;',
          '0': 0
        };
        delete icons['0'];
        window.icomoonLiga = function (els) {
            var classes,
                el,
                i,
                innerHTML,
                key;
            els = els || document.getElementsByTagName('*');
            if (!els.length) {
                els = [els];
            }
            for (i = 0; ; i += 1) {
                el = els[i];
                if (!el) {
                    break;
                }
                classes = el.className;
                if (/icon/.test(classes)) {
                    innerHTML = el.innerHTML;
                    if (innerHTML && innerHTML.length > 1) {
                        for (key in icons) {
                            if (icons.hasOwnProperty(key)) {
                                innerHTML = innerHTML.replace(new RegExp(key, 'g'), icons[key]);
                            }
                        }
                        el.innerHTML = innerHTML;
                    }
                }
            }
        };
        window.icomoonLiga();
    }
}());
