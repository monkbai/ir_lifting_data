from os import path
from os import system
from subprocess import Popen

from src.utils.config import ps_threshold, ida_pro_path
from src.utils.log import *


def radiff2_cmp_bins(bin1: str, bin2: str):
    output_file = './bins/' + bin1.split('_')[-1] + 'vs' + bin2.split('_')[-1] + '.sim'
    with open(output_file, 'w') as out:
        log('radiff2 -s {} {} > {}'.format(bin1, bin2, output_file), 'RUN CMD')
        p = Popen(['radiff2', '-s', bin1, bin2], stdout=out)
    return p


def ida_bin_export_info(bin_path: str, bin_export_path: str):
    ida_pro = ida_pro_path
    cmd = 'sudo LD_PRELOAD=/home/hwangdz/git/libfaketime/src/libfaketime.so.1 FAKETIME=\"2019-07-01 00:00:00\" TVHEADLESS=1 {} -A -OBinExportModule:{} -OBinExportAlsoLogToStdErr:FALSE -OBinExportAutoAction:BinExportBinary {}'.format(
        ida_pro,
        bin_export_path,
        bin_path
    )
    log(cmd, LogType.RUN_CMD)
    return system(cmd)


def bindiff_similarity(bin_export1: str, bin_export2: str, out_dir='/tmp', outfile=None):
    bindiff = '/opt/bindiff/bin/bindiff'
    bin1_basename = (path.basename(bin_export1)).split('.')[0]
    bin2_basename = (path.basename(bin_export2)).split('.')[0]
    cmd = "sudo LD_PRELOAD=/home/hwangdz/git/libfaketime/src/libfaketime.so.1 FAKETIME=\"2019-07-01 00:00:00\" {} --primary={} --secondary={} --output_dir={}".format(
        bindiff, bin_export1, bin_export2, out_dir)
    if outfile is not None:
        cmd += ' > ' + outfile
    log(cmd, LogType.RUN_CMD)
    ret = system(cmd)
    output_file_basename = bin1_basename + '_vs_' + bin2_basename + '.BinDiff'
    output_file = path.join(path.abspath(out_dir), output_file_basename)
    return ret, output_file


def read_bindiff_export(bindiff_file_path: str, output_file=None):
    sqlite3 = 'sqlite3'
    sql_instr = 'SELECT similarity, confidence FROM metadata;'
    cmd = '{} {} \"{}\"'.format(sqlite3, bindiff_file_path, sql_instr)
    if output_file is None:
        output_file = '/tmp/read_bindiff_export_' + path.basename(bindiff_file_path)
    else:
        output_file = path.abspath(output_file)
    cmd += ' > ' + output_file
    log(cmd, LogType.RUN_CMD)
    ret = system(cmd)
    assert ret == 0
    with open(output_file, 'r') as sim_cfd:
        line = sim_cfd.read()
        es = line.split('|')
        similarity = float(es[0])
        confidence = float(es[1])
        return similarity, confidence


def radiff2_cmp_all_bins(bins: list):
    running_ps = []
    for i in range(len(bins)):
        for j in range(i + 1, len(bins)):
            p = radiff2_cmp_bins(bins[i], bins[j])
            running_ps.append(p)
            if len(running_ps) == ps_threshold:
                for p in running_ps:
                    p.wait()
                    running_ps.remove(p)
                    break
    for p in running_ps:
        p.wait()


def get_bindiff_similarity(bin1, bin2):
    ida_bin_export_info(bin1, bin1 + '.binExport')
    ida_bin_export_info(bin2, bin2 + '.binExport')
    bin1_basename = (path.basename(bin1))
    bin2_basename = (path.basename(bin2))
    output_file_basename = '/tmp/' + bin1_basename + '_vs_' + bin2_basename + '.BinDiff'
    bindiff_similarity(bin1 + '.binExport', bin2 + '.binExport')
    similarity_score, confidence_score = read_bindiff_export(output_file_basename)
    print("s:%f, c:%f" % (similarity_score, confidence_score))
    return similarity_score, confidence_score
