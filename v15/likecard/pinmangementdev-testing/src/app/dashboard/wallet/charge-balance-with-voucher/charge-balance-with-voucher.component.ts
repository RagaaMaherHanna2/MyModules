import { Component } from '@angular/core';
import { FormBuilder, Validators } from '@angular/forms';
import { Store } from '@ngrx/store';
import { WalletService } from 'src/app/services/wallet/wallet.service';
import { environment } from 'src/environments/environment';
import { closeLoadingDialog, openLoadingDialog } from 'src/store/loadingSlice';

@Component({
  selector: 'app-charge-balance-with-voucher',
  templateUrl: './charge-balance-with-voucher.component.html',
  styleUrls: ['./charge-balance-with-voucher.component.scss'],
})
export class ChargeBalanceWithVoucherComponent {
  userCurrency: string = (localStorage.getItem(environment.CURRENCY_SYMBOL)|| 'null')

  codeForm = this.formBuilder.group({
    code: ['', Validators.required],
  });
  codes = [
    {
      amount: 163,
      alphanumeric: 'XMPZ-ZCKF-FKRL-MXWY',
    },
    {
      amount: 730,
      alphanumeric: 'TZVM-DPDW-CPFQ-QPKR',
    },
    {
      amount: 848,
      alphanumeric: 'NLPT-WPHB-JPPJ-YNDY',
    },
    {
      amount: 252,
      alphanumeric: 'ZGVY-CBTX-TMBG-QTRP',
    },
    {
      amount: 242,
      alphanumeric: 'PJYJ-CKHW-FPLV-RHYG',
    },
    {
      amount: 521,
      alphanumeric: 'FHWK-JYFP-RLRB-XLTJ',
    },
    {
      amount: 394,
      alphanumeric: 'TBCP-PXMP-CXNQ-JRYN',
    },
    {
      amount: 165,
      alphanumeric: 'DKTH-NCRD-DTMD-HTGQ',
    },
    {
      amount: 622,
      alphanumeric: 'HRSD-JJKX-NWFV-GNJM',
    },
    {
      amount: 836,
      alphanumeric: 'TRMM-JXNY-YJCV-CNKR',
    },
    {
      amount: 384,
      alphanumeric: 'WTBW-RKGJ-WSCC-NMCH',
    },
    {
      amount: 832,
      alphanumeric: 'KJXV-MHMQ-LPYQ-CPFG',
    },
    {
      amount: 586,
      alphanumeric: 'CBJY-MSKV-LHGS-HJFZ',
    },
    {
      amount: 212,
      alphanumeric: 'NZRJ-CWKT-FTDJ-QNWD',
    },
    {
      amount: 775,
      alphanumeric: 'WRVV-SXDJ-LGJF-NFWQ',
    },
    {
      amount: 935,
      alphanumeric: 'WCWF-FJYW-PLBF-VRYW',
    },
    {
      amount: 420,
      alphanumeric: 'RMKV-XKFN-SGCJ-VSNV',
    },
    {
      amount: 255,
      alphanumeric: 'TTHJ-CRDW-RPDS-PCYY',
    },
    {
      amount: 139,
      alphanumeric: 'MZLD-SFKQ-ZJJS-CNCR',
    },
    {
      amount: 536,
      alphanumeric: 'GWKQ-XRHC-SBQP-JVGK',
    },
    {
      amount: 803,
      alphanumeric: 'YYKQ-SYLV-MXMM-CLVP',
    },
    {
      amount: 115,
      alphanumeric: 'WJVY-QZKK-QDRX-VFBC',
    },
    {
      amount: 519,
      alphanumeric: 'YTXG-FZZQ-XVMD-MKYR',
    },
    {
      amount: 544,
      alphanumeric: 'QDHK-KSVR-XJRT-SFHH',
    },
    {
      amount: 597,
      alphanumeric: 'XXGX-VXLN-HQWY-CZVY',
    },
    {
      amount: 211,
      alphanumeric: 'WQCL-YJDJ-GPDJ-QYDW',
    },
    {
      amount: 541,
      alphanumeric: 'FHXS-JFRG-SLFD-QVHX',
    },
    {
      amount: 593,
      alphanumeric: 'VFJW-WMWW-KRWP-NKKN',
    },
    {
      amount: 848,
      alphanumeric: 'NTFJ-SQGC-SLWP-DXSW',
    },
    {
      amount: 919,
      alphanumeric: 'JTJM-XVZY-XTPJ-RLWW',
    },
    {
      amount: 338,
      alphanumeric: 'XXNC-JDHY-MVRX-XCHD',
    },
    {
      amount: 870,
      alphanumeric: 'CGCG-ZQDR-XBTW-JTXS',
    },
    {
      amount: 127,
      alphanumeric: 'MJBK-NLXT-CSMS-BXTD',
    },
    {
      amount: 580,
      alphanumeric: 'XYJD-VBFC-YNXL-KMZH',
    },
    {
      amount: 189,
      alphanumeric: 'RGBC-RKZT-JFCM-LMGF',
    },
    {
      amount: 525,
      alphanumeric: 'GVSS-CPFD-BMMF-SRVP',
    },
    {
      amount: 254,
      alphanumeric: 'NJXT-HQCZ-WDWS-GRHD',
    },
    {
      amount: 378,
      alphanumeric: 'ZGCK-RJQK-BZDK-BQWW',
    },
    {
      amount: 861,
      alphanumeric: 'SQTS-WHQQ-TJWK-FYPZ',
    },
    {
      amount: 273,
      alphanumeric: 'RNVW-KDGQ-QBRD-NMJZ',
    },
    {
      amount: 710,
      alphanumeric: 'JQYY-ZBCR-TFKQ-MXNV',
    },
    {
      amount: 235,
      alphanumeric: 'CVSV-MNGR-YXMJ-TCKL',
    },
    {
      amount: 204,
      alphanumeric: 'KBJX-NCYK-MKCQ-DGWR',
    },
    {
      amount: 787,
      alphanumeric: 'TCLG-KMXW-NSQC-NYYL',
    },
    {
      amount: 194,
      alphanumeric: 'VKFF-KWSY-WRMK-HWMS',
    },
    {
      amount: 904,
      alphanumeric: 'KKQN-MRDZ-RRFN-XZJR',
    },
    {
      amount: 902,
      alphanumeric: 'SMQF-QCCY-XNGL-HYXP',
    },
    {
      amount: 888,
      alphanumeric: 'MRXR-QMZP-DCQG-KDTD',
    },
    {
      amount: 736,
      alphanumeric: 'JLLJ-LQNW-LMSY-WYQZ',
    },
    {
      amount: 902,
      alphanumeric: 'VGJS-JPKD-LZCZ-RWZX',
    },
    {
      amount: 850,
      alphanumeric: 'LRYR-NFGT-GYJZ-FLCG',
    },
    {
      amount: 606,
      alphanumeric: 'SCBR-CVQF-YCGW-QWLP',
    },
    {
      amount: 535,
      alphanumeric: 'TLMW-YNDV-SVTW-SLYC',
    },
    {
      amount: 217,
      alphanumeric: 'ZYHL-JFNJ-TDJW-ZNVD',
    },
    {
      amount: 561,
      alphanumeric: 'LWFZ-KNKN-KMDZ-VBTW',
    },
    {
      amount: 119,
      alphanumeric: 'VCLW-FGRN-WTCR-DJPT',
    },
    {
      amount: 181,
      alphanumeric: 'FGKX-YFNR-VFWY-QYYD',
    },
    {
      amount: 708,
      alphanumeric: 'NMKV-XTKM-FVMY-PPYJ',
    },
    {
      amount: 730,
      alphanumeric: 'NZTX-BVBD-KGQM-PSGV',
    },
    {
      amount: 393,
      alphanumeric: 'YMGR-RDTP-SVPX-NPTJ',
    },
    {
      amount: 365,
      alphanumeric: 'KJSJ-ZXRW-LNXP-JXVX',
    },
    {
      amount: 919,
      alphanumeric: 'YKPQ-GRGN-FKYB-WQYH',
    },
    {
      amount: 803,
      alphanumeric: 'GXQK-JJJP-GHFK-FVRS',
    },
    {
      amount: 210,
      alphanumeric: 'WSLG-TZLX-RGGR-KQPT',
    },
    {
      amount: 563,
      alphanumeric: 'KYVY-VLHT-YMMP-VTNK',
    },
    {
      amount: 879,
      alphanumeric: 'YHWR-NNTR-QBCD-YXWT',
    },
    {
      amount: 610,
      alphanumeric: 'FLWJ-SPJR-KWGC-FKPH',
    },
    {
      amount: 842,
      alphanumeric: 'HVHY-ZKNF-GQMY-YWFR',
    },
    {
      amount: 624,
      alphanumeric: 'FTPN-JVCY-WBZR-KPPG',
    },
    {
      amount: 486,
      alphanumeric: 'RFTL-GJYT-QWPR-DYDW',
    },
    {
      amount: 675,
      alphanumeric: 'TZPP-JBYK-VPJJ-VMLV',
    },
    {
      amount: 307,
      alphanumeric: 'XCTR-GMMC-KPVC-JDNS',
    },
    {
      amount: 457,
      alphanumeric: 'RDKT-QVCJ-QKJY-WYWH',
    },
    {
      amount: 457,
      alphanumeric: 'TNNG-MPCD-QNSN-NDWD',
    },
    {
      amount: 799,
      alphanumeric: 'WZSD-FDMG-BQTL-RKNM',
    },
    {
      amount: 790,
      alphanumeric: 'PHYH-KWJD-YNQN-TDQD',
    },
    {
      amount: 124,
      alphanumeric: 'SLYW-KMCQ-BSFV-SXML',
    },
    {
      amount: 520,
      alphanumeric: 'JRFM-KMYL-JDNW-KFCF',
    },
    {
      amount: 377,
      alphanumeric: 'ZDWQ-KCFZ-LZVS-WXFB',
    },
    {
      amount: 980,
      alphanumeric: 'CJMH-JSWY-DCGR-LCYV',
    },
    {
      amount: 865,
      alphanumeric: 'NMGG-HXXC-KMKJ-XGPR',
    },
    {
      amount: 757,
      alphanumeric: 'VRQF-DLHQ-PKCP-DVXK',
    },
    {
      amount: 131,
      alphanumeric: 'CPLL-LSZP-YLNG-GQWF',
    },
    {
      amount: 281,
      alphanumeric: 'ZTVY-PJNM-HHJS-LZRQ',
    },
    {
      amount: 531,
      alphanumeric: 'PNQP-VDGJ-PBPN-QVTW',
    },
    {
      amount: 980,
      alphanumeric: 'SYDB-YYRV-VRZL-LWSP',
    },
    {
      amount: 519,
      alphanumeric: 'VCMD-QLDV-HSCW-HKKZ',
    },
    {
      amount: 951,
      alphanumeric: 'TQRV-NCMF-RSCF-VYYL',
    },
    {
      amount: 301,
      alphanumeric: 'RTDM-NPRF-RSDJ-XPPZ',
    },
    {
      amount: 491,
      alphanumeric: 'YXRF-DGNK-HTZL-XDWT',
    },
    {
      amount: 199,
      alphanumeric: 'PKDR-CPBW-KTFM-KVTH',
    },
    {
      amount: 680,
      alphanumeric: 'JZTG-ZYTJ-MXNH-PXLP',
    },
    {
      amount: 562,
      alphanumeric: 'HMSG-DFTG-JPFP-TQJH',
    },
    {
      amount: 350,
      alphanumeric: 'DLJC-MMCK-WTYW-HXRS',
    },
    {
      amount: 932,
      alphanumeric: 'HTVY-GKJT-YZFS-SCKD',
    },
    {
      amount: 152,
      alphanumeric: 'VJGR-TCFT-FYYG-YZRD',
    },
    {
      amount: 232,
      alphanumeric: 'KMWQ-FQVW-HCTG-WNPQ',
    },
    {
      amount: 727,
      alphanumeric: 'LQHF-HQXW-GQQC-HCKX',
    },
    {
      amount: 133,
      alphanumeric: 'DSSH-NNVT-CMBK-RYGP',
    },
    {
      amount: 129,
      alphanumeric: 'RQSH-YDCR-PNLM-SCNX',
    },
  ];
  res: {
    status: string;
    class: string;
    amount: number;
  };
  showRes = false;
  constructor(
    private formBuilder: FormBuilder,
    private walletService: WalletService,
    private store: Store
  ) {}
  onSubmit(event: SubmitEvent): void {
    event.preventDefault();
    this.showRes = false;
    this.store.dispatch(openLoadingDialog());
    const result = this.codes.find(
      (code) => code.alphanumeric === this.codeForm.value.code!
    );

    if (result) {
      const amount = result.amount + (100 - (result.amount % 100));
      this.res = {
        status: $localize`success`,
        class: 'success',
        amount,
      };
      const balance = localStorage.getItem(environment.BALANCE_KEY) ?? 0;
      localStorage.setItem(environment.BALANCE_KEY, `${amount + +balance}`);
      this.walletService.updateUserBalance();
      setTimeout(() => {
        this.store.dispatch(closeLoadingDialog());
        this.showRes = true;
      }, 1000);
    } else {
      setTimeout(() => {
        this.res = {
          status: $localize`failed`,
          class: 'failed',
          amount: 0,
        };

        this.showRes = true;
        this.store.dispatch(closeLoadingDialog());
      }, 1000);
    }
  }
}
