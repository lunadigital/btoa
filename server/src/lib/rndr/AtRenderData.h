#pragma once

#include "AtAov.h"

namespace arnoldserver {
namespace rndr {

    class AtRenderData {
        protected:
            AtAov* aovs;
            int size;

        public:
            AtRenderData();
            ~AtRenderData();

            AtAov* add(std::string, int, int, int);

            AtAov* findAovByIndex(int);
            AtAov* findAovByName(std::string);
            
            int getAovIndex(AtAov&);
            int getAovIndex(std::string);
    };

}
}