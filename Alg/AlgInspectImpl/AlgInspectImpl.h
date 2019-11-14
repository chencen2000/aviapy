/*********************************************************************************
  *Copyright(C),2018-2021,Bozhon
  *FileName:     AlgInspectImpl.h
  *Author:       HaoChang
  *Version:      V1.0
  *Date:         2018-01-10
  *Description:  动态外部算法动态库
  *History:      修改历史记录列表，每条修改记录应包含修改日期、修改者及修改内容简介
**********************************************************************************/

#include<map>
#include<memory>
#include"AlgInspectBase.h"

#ifdef ALGINSPECT_EXPORT                   //导出宏
#define DLL_EXPORT __declspec(dllexport)
#else
#define DLL_EXPORT __declspec(dllimport)
#endif

//API for AlgProcessing  CH20190118

extern "C" DLL_EXPORT CreateAlgFunction GetAlgInspRegistFunctionPt();   //检测对象注册指针
extern "C" DLL_EXPORT char* GetAlgInspRegistAlgName();                  //检测类名接口
//因为使用了QT功能调试信息输出，需包含Qt5Cored.dll Qt5Guid.dll Qt5Widgetsd.dll,否则加载失败
