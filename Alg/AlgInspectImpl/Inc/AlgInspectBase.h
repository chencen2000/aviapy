#ifndef ALGINSPECTBASE_H
#define ALGINSPECTBASE_H


#include "AlgDataType.h"
#include<memory>
#include<map>
#include <HalconCpp.h>
#include"QtFileOperate.h"


using namespace HalconCpp;

class stag_HRegionRuns
{
public:
    stag_HRegionRuns()
    {

    }
	~stag_HRegionRuns()
	{
		Clear();
	}
    stag_HRegionRuns(HObject& hreg)
    {
        if(hreg.IsInitialized())
        {
            HObject tempReg;
            HTuple hvArea;
            AreaCenter(hreg,&hvArea,NULL,NULL);
            if(hvArea.Length()>0&&hvArea[0].D()>0)
            {
                Union1(hreg,&tempReg);
                GetRegionRuns(tempReg,&rows,&colstart,&colend);
            }
        }
    }
    stag_HRegionRuns(stag_HRegionRuns& runs)
    {
        rows=runs.rows;
        colstart=runs.colstart;
        colend=runs.colend;
        vrect.assign(runs.vrect.begin(),runs.vrect.end());

    }
    stag_HRegionRuns& operator =(stag_HRegionRuns& runs)
    {
        rows=runs.rows;
        colstart=runs.colstart;
        colend=runs.colend;
        vrect.assign(runs.vrect.begin(),runs.vrect.end());
        return *this;
    }
    void AddArect(ARect& rect)
    {
        if(rect.valid())
        {
          vrect.push_back(rect);
        }
    }
    HObject convertToregion()
    {
        HObject hregion;
        GenRegionRuns(&hregion,rows,colstart,colend);
        return hregion;
    }
    void Clear()
    {
        rows.Clear();
        colstart.Clear();
        colend.Clear();
        vrect.clear();

    }
    HTuple rows;
    HTuple colstart;
    HTuple colend;
    std::vector<ARect> vrect;

};


#define DebugPushRegion(reg) \
    if(ptMapResult!=nullptr){(*ptMapResult)[#reg]=stag_HRegionRuns(reg);}

#define DebugPushNameRegion(strname,reg) \
    if(ptMapResult!=nullptr){(*ptMapResult)[strname]=stag_HRegionRuns(reg);}

#define RegisterAlgInsp(AlgName) \
int s_Params::snId = 0;\
static std::shared_ptr<CAlgInspectorBase> CreateAlgInsp()\
{\
     return std::make_shared<AlgName>();\
}\
static char strAlgName[]=#AlgName;\
CreateAlgFunction GetAlgInspRegistFunctionPt()\
{\
        return CreateAlgInsp;\
}\
 char*  GetAlgInspRegistAlgName()\
{\
   return strAlgName;\
}



class CAlgInspectorBase
{
public:
	CAlgInspectorBase() {}

	virtual ~CAlgInspectorBase() {}
	//系统初始化
	virtual bool Init(const s_AlgInitParam & sAlgInitParam) = 0;

    //检测函数
    virtual bool  GCheck(const s_AlgCheckInputParam &sAlgCheckInputParam, s_AlgCheckOutputParam &sAlgCheckOutputResult, int nGroupId, const sInspParams* pAlgParam, std::map<std::string,stag_HRegionRuns>* ptMapResult) = 0;

	//参数对话框
	virtual s_StatusModelDlg CallAlgModelDlg() = 0;

	//更新参数,根据配置文件信息决定1：加载模板 2：加载参数 ；约束：调用者保证UpdateAlgParam和GCheck串行调用
	virtual bool UpdateAlgParam() = 0;

	//系统退出，释放资源
	virtual bool Free() = 0;

	//获取最后的状态信息
	virtual const s_AlgErrorInfo &GetLastStatus() = 0;
};


typedef std::shared_ptr<CAlgInspectorBase>(*CreateAlgFunction)();
typedef CreateAlgFunction(*GetAlgInspRegFunction)();
typedef char*(*GetAlgInspNameFun)();
#endif // ALGINSPECTBASE_H


