// Historia odcinków i rejestr tematów
const PODCAST_HISTORY = [
  {
    "episode": 1,
    "topic": "Sztuka słuchania się w związku",
    "date": "2026-10-26T05:27:24.306497",
    "duration_sec": 157.3,
    "duration_min": 2.62,
    "video_file": "podcast_ep1_20261026_052551.mp4",
    "thumbnail_file": "thumb_ep1_20261026_052551.jpg",
    "platform": "Local"
  },
  {
    "episode": 2,
    "topic": "Sekrety budowania intymności po latach razem",
    "date": "2026-10-29T02:42:41.502722",
    "duration_sec": 151.9,
    "duration_min": 2.53,
    "video_file": "podcast_ep2_20261029_024135.mp4",
    "thumbnail_file": "thumb_ep2_20261029_024135.jpg",
    "platform": "Facebook"
  },
  {
    "episode": 3,
    "topic": "Granice w miłości: jak powiedzieć 'nie', by wzmocnić 'tak'",
    "date": "2026-10-29T07:55:40.562308",
    "duration_sec": 1166.75,
    "duration_min": 19.45,
    "video_file": "podcast_ep3_20261029_074410.mp4",
    "thumbnail_file": "thumb_ep3_20261029_074410.jpg",
    "platform": "Facebook"
  }
];
if (typeof module !== 'undefined' && module.exports) { module.exports = PODCAST_HISTORY; }
if (typeof window !== 'undefined') { window.PODCAST_HISTORY = PODCAST_HISTORY; }
