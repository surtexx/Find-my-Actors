document.addEventListener('DOMContentLoaded', function () {
    new Splide('#image-carousel', {
      type: 'slide',
      perPage: 1,
      arrows: true,
      rewind: true,
    }).mount();
  });
  