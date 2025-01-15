
var s;

document.addEventListener('DOMContentLoaded', function() {

  s = new Slideshow(".content-container.gallery .slide");
  se = new SlideshowEvents(s);

  var doAction = function(action) {
    return function() {
        window.scrollTo(0, 0);
        action();
    }
  }

  se.bindKey(se.KEY_LEFT, doAction(se.ACTION_PREV));
  se.bindKey(se.KEY_RIGHT, doAction(se.ACTION_NEXT));

  se.bindElement('.content-container.gallery .controls .previous', doAction(se.ACTION_PREV));
  se.bindElement('.content-container.gallery .controls .next', doAction(se.ACTION_NEXT));

  se.bindEvent(se.EVENT_HASHCHANGE, doAction(se.ACTION_HASHCHANGE));

  se.bindTouch(".content-container.gallery");


  /* change up some website styles depending on which slide is being shown */
  var callback = function(slide) {
    var titleTag = document.querySelector('.content-container.gallery .caption .title');
    var captionTag = document.querySelector('.content-container.gallery .caption .description');
    var contentTag = document.querySelector('.content-container.gallery .caption .content');

    var title = slide.getAttribute('data-title');
    var caption = slide.getAttribute('data-caption');
    var content = slide.getAttribute('data-content');

    titleTag.textContent = title;
    captionTag.textContent = caption;
    contentTag.textContent = content;

  }

  s.bind('advance', callback);
  s.showSlide(se.selectedSlide());


}, false);
