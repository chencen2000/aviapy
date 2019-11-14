#ifndef ALGPARAMBASE_H
#define ALGPARAMBASE_H

#include <string>
#include <vector>
#include <map>
#include <windows.h>
#include "AlgDataType.h"

#pragma execution_character_set("utf-8")


/*参数基类*/
class CAlgParamBase
{
public:
    CAlgParamBase(){};
     ~CAlgParamBase() {}
     virtual std::string* GetParamName()=NULL;
     virtual std::map<std::string,s_Params>* GetParamVector()=NULL;
     bool Init();
     bool Init(const std::string &strParamName);
     bool Init(const std::string &strParamName, const std::string &strParamPath);
     bool SetParam(CAlgParamBase& param);
     bool SetRoi(const ARect& rect);
     bool ReadParam(const std::string& strParamPath);        //读取参数
     bool WriteParam(const std::string& strParamPath);     //写入参数
     bool ResetParam();     //重置参数
	 sInspParams* GetInspParams();  
private:
	 sInspParams m_sInspParams;//检测参数封装
};
typedef std::shared_ptr<CAlgParamBase>(*CreateAlgParamFunction)();
typedef std::map<std::string, CreateAlgParamFunction> CreateAlgParamMap;
typedef std::map<std::string, std::string> AlgParamNameMap;


typedef CreateAlgParamFunction(*GetAlgParamRegFunction)();
typedef char*(*GetAlgParamNameFun)();


#define RegParam(BaseValue,MaxValue,MinValue,Name,Info,EnName)\
    {EnName,s_Params(BaseValue,MaxValue,MinValue,Name,Info)}

/*声明参数类宏定义*/
#define DeclareAlgParamStart(AlgName) \
AlgNameClrearId AlgName##temp;\
class AlgName##Param :public CAlgParamBase{ \
 public: /* NOLINT */ \
  AlgName##Param() {\
  m_vecParams=m_vecBaseParams;\
}; \
  AlgName##Param(const std::map<std::string,s_Params>& vParam) { \
    m_vecParams=vParam;\
    }; \
  ~ AlgName##Param() { }; \
  std::string* GetParamName()\
   {\
    return &m_strAlgName;\
   }\
  std::map<std::string,s_Params>* GetParamVector()\
   {\
    return &m_vecParams;\
   }\
  static std::map<std::string,s_Params> m_vecBaseParams;\
  std::map<std::string,s_Params> m_vecParams;\
  static std::string m_strAlgName;\
}; \
std::string AlgName##Param::m_strAlgName=#AlgName;\
std::map<std::string,s_Params> AlgName##Param::m_vecBaseParams={

#define DeclareAlgParamEnd \
};


/*注册参数管理类*/
#define RegisterAlgParam(AlgName,AlgInfo) \
int s_Params::snId = 0;\
static std::shared_ptr<CAlgParamBase> CreateAlgParam()\
{\
    return std::make_shared<AlgName##Param>();\
}\
CreateAlgParamFunction GetAlgParamRegistFunctionPt()\
{\
    return CreateAlgParam;\
}\
static char strAlgParamName[]=AlgInfo;\
char *GetAlgParamRegistAlgParamName()\
{\
    return strAlgParamName;\
}\
static char strAlgName[]=#AlgName;\
char *GetAlgParamRegistAlgName()\
{\
    return strAlgName;\
}


#endif // ALGPARAMBASE_H


