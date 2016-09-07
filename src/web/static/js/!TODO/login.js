
function success_login(user)
{
    $(".upload-button").fadeIn("slow");
    $("#sign-up").hide();

    window.logged_in = user;
}


function logout(event) {
    $.ajax({
        type: 'GET',
        url: "/logout.json",
        success: function(data)
        {
            if (data.error)
            {
                // Do not fire event
            }
            else
            {
                window.logged_in = false;
                event();

                $('.top-right').notify({
                    type: 'success',
                    message: { text: "Successfully logged out" },
                    fadeOut: { enabled: true, delay: 5000 }
                }).show();

                window.snapper.disable();
            }

        }
    });
}