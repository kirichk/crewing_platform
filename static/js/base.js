jQuery('#id_title').on('change', () => {
    // You can also do this with document.querySelector('')
    if ($('#id_title option:selected').text() == 'Другое') {
        jQuery('.titlespecify').show();
    } else {
        jQuery('.title1specify').hide();
    }
});
