//
//  MainView.swift
//  bulls
//
//  Created by 차차 on 9/20/24.
//

import SwiftUI

@available(iOS 15.0, *)
struct MainView: View {
    @State private var selectedTab: Int = 0
    @State private var showAlert = false
    
    
    
    @available(iOS 15.0, *)
    var body: some View {
        ZStack {
            if #available(iOS 15.0, *) {
                Rectangle()
                    .foregroundStyle(Color.blue)
                    .ignoresSafeArea()
            } else {
                // Fallback on earlier versions
            }
            
                VStack {
                    Text("스마트 조명 관리 시스템")
                        .foregroundStyle(Color.white)
                        .font(.system(size: 20, weight: .black))
                        .padding(.vertical, 20)
                    
                    VStack(spacing: 30) {
                        HStack(spacing: 0) {
                            Button(action: {
                                selectedTab = 0
                            }) {
                                Text("현재 조명")
                                    .foregroundStyle(.black)
                                    .frame(maxWidth: .infinity)
                                    .padding(10)
                                    .background(selectedTab == 0 ? Color.white : Color.white.opacity(0.5))
                                    .cornerRadius(25, corners: [.topLeft, .topRight])
                            }
                            
                            Button(action: {
                                selectedTab = 1
                            }) {
                                Text("시나리오")
                                    .foregroundStyle(.black)
                                    .frame(maxWidth: .infinity)
                                    .padding(10)
                                    .background(selectedTab == 1 ? Color.white : Color.white.opacity(0.5))
                                    .cornerRadius(25, corners: [.topLeft, .topRight])
                                
                            }
                        }
                        .background(Color.blue)
                        
                        VStack {
                            if selectedTab == 0 {
                                LightSettingView(showAlert: $showAlert)
                                    .padding(.horizontal, 5)
                            }
                            else {
                                ScenarioView()
                                    .padding(.horizontal, 5)
                            }
                        }
                        .background(Color.white)
                    }
                    .background(Color.white)
                }
            }
        .alert(isPresented: $showAlert) {
            Alert(title: Text("조명의 설정 값이 변경 되었습니다."), message: nil,
                          dismissButton: .default(Text("확인")))
        }
    }
}

extension View {
    func cornerRadius(_ radius: CGFloat, corners: UIRectCorner) -> some View {
        clipShape(RoundedCorner(radius: radius, corners: corners))
    }
}
