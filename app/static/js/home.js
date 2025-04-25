$(document).ready(function () {
    // Fetch moods
    $.ajax({
      url: "/api/user_moods",
      method: "GET",
      success: function (data) {
        data.forEach(function (item) {
          $("#moodList").append(
            `<li class="border p-2 rounded bg-blue-100">
               <strong>${item.mood}</strong> at ${new Date(item.timestamp).toLocaleString()}
             </li>`
          );
        });
      },
    });
  
    // Fetch friends
    $.ajax({
      url: "/api/friends",
      method: "GET",
      success: function (data) {
        data.forEach(function (friend) {
          $("#friendsList").append(
            `<li class="p-2 bg-white rounded shadow">${friend}</li>`
          );
        });
      },
    });
  });