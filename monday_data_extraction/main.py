import pdf_gen, data_to_score, data_to_chart, monday


def genera_report_hf():


    # DATI data_to_score

    prev_evasi_mes = data_to_score.n_tot_prev_evasi_mese()
    prev_acc_mes = data_to_score.n_tot_prev_accettati_mese()
    prev_acc_consuntivo = data_to_score.prev_acc_consuntivo()
    prev_acc_anno = data_to_score.n_tot_prev_accettati_anno()
    importo_tot_prev_evasi = data_to_score.importo_tot_prev_evasi()
    importo_tot_prev_accettati = data_to_score.importo_tot_prev_accettati()
    fatturato_prev_2023 = data_to_score.fatturato_prev_2023()
    fatturato_ad_oggi = data_to_score.fatturato_ad_oggi()
    fatturato_da_emettere = data_to_score.fatturato_da_emettere()


    # DATI data_to_chart

    chart_progetti_in_progress_su_pm = data_to_chart.n_progetti_in_progress_su_pm()
    importo_progetti_progress_anno = data_to_chart.importo_progetti_progress_anno()
    portafoglio_ordine_residuo = data_to_chart.portafoglio_ordine_residuo()
    analisi_ferie_malattia = data_to_chart.analisi_ferie_malattia()
    analisi_permessi_rol = data_to_chart.analisi_permessi_rol()
    analisi_assenze_liberi_professionisti = data_to_chart.analisi_assenze_liberi_professionisti()
    giornate_smart_working = data_to_chart.giornate_smart_working()
    timesheet_mese = data_to_chart.timesheet_mese()
    bu_h_pie = data_to_chart.bu_h_pie()



    pdf = pdf_gen.generate_pdf(prev_evasi_mes,
                               prev_acc_mes,
                               prev_acc_consuntivo,
                               importo_tot_prev_evasi,
                               prev_acc_anno,
                               importo_tot_prev_accettati,
                               fatturato_prev_2023,
                               fatturato_ad_oggi,
                               fatturato_da_emettere,
                               chart_progetti_in_progress_su_pm,
                               importo_progetti_progress_anno,
                               portafoglio_ordine_residuo,
                               analisi_ferie_malattia,
                               analisi_permessi_rol,
                               analisi_assenze_liberi_professionisti,
                               giornate_smart_working,
                               timesheet_mese,
                               bu_h_pie
                               )

    return(pdf)

genera_report_hf()

def invia_mail(pdf):
    """

    :param pdf:
    :return:
    """

    #funzione_per_inviare_mail




# pdf = genera_report_hf()
# invia_mail(pdf)
