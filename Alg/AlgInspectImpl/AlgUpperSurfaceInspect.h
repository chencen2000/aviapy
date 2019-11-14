/*********************************************************************************
  *Copyright(C),2018-2021,Bozhon
  *FileName:     AlgUpperSurfaceInspect.h
  *Author:       HaoChang
  *Version:      V1.0
  *Date:         2018-01-10
  *Description:  检测算法，在此基础上添加GCheck相关检测功能
  *History:      修改历史记录列表，每条修改记录应包含修改日期、修改者及修改内容简介
**********************************************************************************/

#ifndef ALGUPPERSURFACEINSPECT_H
#define ALGUPPERSURFACEINSPECT_H

/*20181218*/
#include "AlgInspectBase.h"

class CAlgDarkDefectInspect: public CAlgInspectorBase
{
public:
    CAlgDarkDefectInspect();

    //系统初始化
    bool Init(const s_AlgInitParam & sAlgInitParam);
	
    //检测函数
    bool  GCheck(const s_AlgCheckInputParam &sAlgCheckInputParam, s_AlgCheckOutputParam &sAlgCheckOutputResult,int nGroupId,const sInspParams* pAlgParam, std::map<std::string,stag_HRegionRuns>* ptMapResult);

    bool GetRectangleCor(HTuple fLen1, HTuple fLen2, HTuple fPhi, HTuple hv_CenterX, HTuple hv_CenterY, ParARect &rect,double fzoomrat);
    //参数对话框
    s_StatusModelDlg CallAlgModelDlg();

    //更新参数,根据配置文件信息决定1：加载模板 2：加载参数 ；约束：调用者保证UpdateAlgParam和GCheck串行调用
    bool UpdateAlgParam();

    //系统退出，释放资源
    bool Free();

    //获取最后的状态信息
    const s_AlgErrorInfo &GetLastStatus();
private:
    void OutPutDefInfo(HObject hv_DefRegions, std::string strDefName, int nInspId, int nPage, std::vector<s_AlgDefectInfo> *pVDefect);

    void CompImage (HObject ho_Image, HObject *ho_ImageMax, HTuple hv_dy, HTuple hv_dx,
        HTuple hv_nLayer);
    void Inter_Distance_Select (HObject ho_Region, HObject *ho_Scraches, HTuple hv_Distance);
    s_AlgErrorInfo m_sAlgErrorInfo;
    stag_HRegionRuns m_HregionRuns;
};


#endif // ALGUPPERSURFACEINSPECT_H
