document.getElementById('show_register').addEventListener('click', function() {
    document.getElementById('login_form').style.display = 'none';
    document.getElementById('register_form').style.display = 'block';
});

document.getElementById('show_login').addEventListener('click', function() {
    document.getElementById('register_form').style.display = 'none';
    document.getElementById('login_form').style.display = 'block';
});